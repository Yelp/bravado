# -*- coding: utf-8 -*-
"""
The :class:`SwaggerClient` provides an interface for making API calls based on
a swagger spec, and returns responses of python objects which build from the
API response.

Structure Diagram::

        +---------------------+
        |                     |
        |    SwaggerClient    |
        |                     |
        +------+--------------+
               |
               |  has many
               |
        +------v--------------+
        |                     |
        |     Resource        +------------------+
        |                     |                  |
        +------+--------------+         has many |
               |                                 |
               |  has many                       |
               |                                 |
        +------v--------------+           +------v--------------+
        |                     |           |                     |
        |     Operation       |           |    SwaggerModel     |
        |                     |           |                     |
        +------+--------------+           +---------------------+
               |
               |  uses
               |
        +------v--------------+
        |                     |
        |     HttpClient      |
        |                     |
        +---------------------+


To get a client

.. code-block:: python

    client = bravado.client.SwaggerClient.from_url(swagger_spec_url)
"""
import logging

from bravado_core.docstring import create_operation_docstring
from bravado_core.exception import SwaggerMappingError
from bravado_core.formatter import SwaggerFormat  # noqa
from bravado_core.param import marshal_param
from bravado_core.spec import Spec
from six import iteritems, itervalues

from bravado.docstring_property import docstring_property
from bravado.requests_client import RequestsClient
from bravado.swagger_model import Loader
from bravado.warning import warn_for_deprecated_op

log = logging.getLogger(__name__)


CONFIG_DEFAULTS = {
    # See the constructor of :class:`bravado.http_future.HttpFuture` for an
    # in depth explanation of what this means.
    'also_return_response': False,

    # List of callbacks that are executed after the incoming response has been
    # validated and the swagger_result has been unmarshalled.
    #
    # The callback should expect two arguments:
    #   param : incoming_response
    #   type  : subclass of class:`bravado_core.response.IncomingResponse`
    #   param : operation
    #   type  : class:`bravado_core.operation.Operation`
    'response_callbacks': [],
}


class SwaggerClient(object):
    """A client for accessing a Swagger-documented RESTful service.

    :param swagger_spec: :class:`bravado_core.spec.Spec`
    """
    def __init__(self, swagger_spec):
        self.swagger_spec = swagger_spec

    @classmethod
    def from_url(cls, spec_url, http_client=None, request_headers=None,
                 config=None):
        """Build a :class:`SwaggerClient` from a url to the Swagger
        specification for a RESTful API.

        :param spec_url: url pointing at the swagger API specification
        :type spec_url: str
        :param http_client: an HTTP client used to perform requests
        :type  http_client: :class:`bravado.http_client.HttpClient`
        :param request_headers: Headers to pass with http requests
        :type  request_headers: dict
        :param config: Config dict for bravado and bravado_core.
            See CONFIG_DEFAULTS in :module:`bravado_core.spec`.
            See CONFIG_DEFAULTS in :module:`bravado.client`.
        """
        log.debug(u"Loading from %s" % spec_url)
        http_client = http_client or RequestsClient()
        loader = Loader(http_client, request_headers=request_headers)
        spec_dict = loader.load_spec(spec_url)
        return cls.from_spec(spec_dict, spec_url, http_client, config)

    @classmethod
    def from_spec(cls, spec_dict, origin_url=None, http_client=None,
                  config=None):
        """
        Build a :class:`SwaggerClient` from a Swagger spec in dict form.

        :param spec_dict: a dict with a Swagger spec in json-like form
        :param origin_url: the url used to retrieve the spec_dict
        :type  origin_url: str
        :param config: Configuration dict - see spec.CONFIG_DEFAULTS
        """
        http_client = http_client or RequestsClient()

        # Apply bravado config defaults
        config = dict(CONFIG_DEFAULTS, **(config or {}))

        swagger_spec = Spec.from_dict(
            spec_dict, origin_url, http_client, config)
        return cls(swagger_spec)

    def get_model(self, model_name):
        return self.swagger_spec.definitions[model_name]

    def __repr__(self):
        return u"%s(%s)" % (self.__class__.__name__, self.swagger_spec.api_url)

    def __getattr__(self, item):
        """
        :param item: name of the resource to return
        :return: :class:`Resource`
        """
        resource = self.swagger_spec.resources.get(item)
        if not resource:
            raise AttributeError(
                'Resource {0} not found. Available resources: {1}'
                .format(item, ', '.join(dir(self))))

        # Wrap bravado-core's Resource and Operation objects in order to
        # execute a service call via the http_client.
        return ResourceDecorator(resource)

    def __dir__(self):
        return self.swagger_spec.resources.keys()


class ResourceDecorator(object):
    """
    Wraps :class:`bravado_core.resource.Resource` so that accesses to contained
    operations can be instrumented.
    """

    def __init__(self, resource):
        """
        :type resource: :class:`bravado_core.resource.Resource`
        """
        self.resource = resource

    def __getattr__(self, name):
        """
        :rtype: :class:`CallableOperation`
        """
        return CallableOperation(getattr(self.resource, name))

    def __dir__(self):
        """
        Exposes correct attrs on resource when tab completing in a REPL
        """
        return self.resource.__dir__()


class CallableOperation(object):
    """
    Wraps an operation to make it callable and provide a docstring. Calling
    the operation uses the configured http_client.

    :type operation: :class:`bravado_core.operation.Operation`
    """
    def __init__(self, operation):
        self.operation = operation

    @docstring_property(__doc__)
    def __doc__(self):
        return create_operation_docstring(self.operation)

    def __getattr__(self, name):
        """
        Forward requests for attrs not found on this decorator to the delegate.
        """
        return getattr(self.operation, name)

    def construct_request(self, **op_kwargs):
        """
        :param op_kwargs: parameter name/value pairs to passed to the
            invocation of the operation.
        :return: request in dict form
        """
        url = self.operation.swagger_spec.api_url.rstrip('/') + self.path_name
        request = {
            'method': self.operation.http_method.upper(),
            'url': url,
            'params': {},  # filled in downstream
            'headers': self.request_options.get('headers', {}),
        }

        # Copy over optional request options
        for request_option in ('connect_timeout', 'timeout'):
            if request_option in self.request_options:
                request[request_option] = self.request_options[request_option]

        self.construct_params(request, op_kwargs)
        return request

    def construct_params(self, request, op_kwargs):
        """
        Given the parameters passed to the operation invocation, validates and
        marshals the parameters into the provided request dict.

        :type request: dict
        :param op_kwargs: the kwargs passed to the operation invocation
        :raises: SwaggerMappingError on extra parameters or when a required
            parameter is not supplied.
        """
        current_params = self.operation.params.copy()
        for param_name, param_value in iteritems(op_kwargs):
            param = current_params.pop(param_name, None)
            if param is None:
                raise SwaggerMappingError(
                    "{0} does not have parameter {1}"
                    .format(self.operation.operation_id, param_name))
            marshal_param(param, param_value, request)

        # Check required params and non-required params with a 'default' value
        for remaining_param in itervalues(current_params):
            if remaining_param.required:
                raise SwaggerMappingError(
                    '{0} is a required parameter'.format(remaining_param.name))
            if not remaining_param.required and remaining_param.has_default():
                marshal_param(remaining_param, None, request)

    def construct_response_callbacks(self):
        """
        :return: List of combined client wide response callbacks and per
            request callbacks.
        """
        client_wide_callbacks = \
            self.operation.swagger_spec.config['response_callbacks']

        per_request_callbacks = \
            self.request_options.get('response_callbacks', [])

        return client_wide_callbacks + per_request_callbacks

    def __call__(self, **op_kwargs):
        """
        Invoke the actual HTTP request and return a future.

        :rtype: :class:`bravado.http_future.HTTPFuture`
        """
        log.debug(u"%s(%s)" % (self.operation.operation_id, op_kwargs))
        warn_for_deprecated_op(self.operation)
        self.request_options = op_kwargs.pop('_request_options', {})
        request_params = self.construct_request(**op_kwargs)
        config = self.operation.swagger_spec.config
        http_client = self.operation.swagger_spec.http_client

        return http_client.request(
            request_params,
            self.operation,
            response_callbacks=self.construct_response_callbacks(),
            also_return_response=config['also_return_response'])
