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
from bravado_core.docstring import operation_docstring_wrapper

from bravado_core.exception import SwaggerMappingError
from bravado_core.param import marshal_param
from bravado_core.response import unmarshal_response
from bravado_core.spec import Spec
from six import iteritems, itervalues

from bravado.requests_client import RequestsClient
from bravado.swagger_model import Loader
from bravado.warning import warn_for_deprecated_op

log = logging.getLogger(__name__)


class SwaggerClient(object):
    """A client for accessing a Swagger-documented RESTful service.
    """

    def __init__(self, swagger_spec):
        """
        :param swagger_spec: :class:`bravado_core.spec.Spec`
        """
        self.swagger_spec = swagger_spec

    @classmethod
    def from_url(cls, spec_url, http_client=None, request_headers=None,
                 config=None):
        """
        Build a :class:`SwaggerClient` from a url to the Swagger
        specification for a RESTful API.

        :param spec_url: url pointing at the swagger API specification
        :type spec_url: str
        :param http_client: an HTTP client used to perform requests
        :type  http_client: :class:`bravado.http_client.HttpClient`
        :param request_headers: Headers to pass with http requests
        :type  request_headers: dict
        :param config: bravado_core config dict. See
            bravado_core.spec.CONFIG_DEFAULTS
        """
        # TODO: better way to customize the request for api calls, so we don't
        #       have to add new kwargs for everything
        log.debug(u"Loading from %s" % spec_url)
        http_client = http_client or RequestsClient()
        loader = Loader(http_client, request_headers=request_headers)
        spec_dict = loader.load_spec(spec_url)
        return cls.from_spec(spec_dict, spec_url, http_client, config)

    @classmethod
    def from_spec(cls, spec_dict, origin_url=None, http_client=None,
                  config=None):
        """
        Build a :class:`SwaggerClient` from swagger api docs

        :param spec_dict: a dict with a Swagger spec in json-like form
        :param origin_url: the url used to retrieve the spec_dict
        :type  origin_url: str
        :param config: Configuration dict - see spec.CONFIG_DEFAULTS
        """
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
            raise AttributeError(u"API has no resource '%s'" % item)

        # Wrap bravado-core's Resource and Operation objects in order to
        # execute a service call via the http_client.
        return ResourceDecorator(resource)

    def __dir__(self):
        return self.swagger_spec.resources.keys()


class ResourceDecorator(object):
    """
    Wraps :class:`bravado_core.resource.Resource` so that accesess to contained
    operations can be instrumented.
    """

    def __init__(self, resource):
        """
        :type resource: :class:`bravado_core.resource.Resource`
        """
        self.resource = resource

    def __getattr__(self, name):
        """
        This actually returns a function because of the unusual way we've
        implemented dynamically generated operation docstrings. See
        operation_docstring_wrapper for the deets.

        :rtype: :class:`OperationDecorator`
        """
        return operation_docstring_wrapper(
            OperationDecorator(getattr(self.resource, name)))


class OperationDecorator(object):
    """
    Enables http_client invocations when the operation is called.
    """

    def __init__(self, operation):
        """
        :type operation: :class:`bravado_core.operation.Operation`
        """
        self.operation = operation

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
        request_options = op_kwargs.pop('_request_options', {})
        url = self.operation.swagger_spec.api_url.rstrip('/') + self.path_name
        request = {
            'method': self.operation.http_method.upper(),
            'url': url,
            'params': {},  # filled in downstream
            'headers': request_options.get('headers', {}),
        }

        # Copy over optional request options
        for request_option in ('connect_timeout', 'timeout'):
            if request_option in request_options:
                request[request_option] = request_options[request_option]

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

    def __call__(self, **op_kwargs):
        """
        Invoke the actual HTTP request and return a future that encapsulates
        the HTTP response.

        :rtype: :class:`bravado.http_future.HTTPFuture`
        """
        log.debug(u"%s(%s)" % (self.operation.operation_id, op_kwargs))
        warn_for_deprecated_op(self.operation)
        request_params = self.construct_request(**op_kwargs)

        def response_callback(response_adapter):
            return unmarshal_response(response_adapter, self)

        return self.operation.swagger_spec.http_client.request(
            request_params, response_callback)
