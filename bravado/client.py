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
from six import iteritems
from six import itervalues

from bravado.config import BravadoConfig
from bravado.config import RequestConfig
from bravado.docstring_property import docstring_property
from bravado.requests_client import RequestsClient
from bravado.swagger_model import Loader
from bravado.warning import warn_for_deprecated_op

log = logging.getLogger(__name__)


class SwaggerClient(object):
    """A client for accessing a Swagger-documented RESTful service.

    :type swagger_spec: :class:`bravado_core.spec.Spec`
    """

    def __init__(self, swagger_spec, also_return_response=False):
        self.__also_return_response = also_return_response
        self.swagger_spec = swagger_spec

    @classmethod
    def from_url(cls, spec_url, http_client=None, request_headers=None, config=None):
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

        :rtype: :class:`bravado_core.spec.Spec`
        """
        log.debug(u"Loading from %s", spec_url)
        http_client = http_client or RequestsClient()
        loader = Loader(http_client, request_headers=request_headers)
        spec_dict = loader.load_spec(spec_url)

        # RefResolver may have to download additional json files (remote refs)
        # via http. Wrap http_client's request() so that request headers are
        # passed along with the request transparently. Yeah, this is not ideal,
        # but since RefResolver has new found responsibilities, it is
        # functional.
        if request_headers is not None:
            http_client.request = inject_headers_for_remote_refs(
                http_client.request, request_headers)

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

        :rtype: :class:`bravado_core.spec.Spec`
        """
        http_client = http_client or RequestsClient()
        config = config or {}

        # Apply bravado config defaults
        bravado_config = BravadoConfig.from_config_dict(config)
        # remove bravado configs from config dict
        for key in set(bravado_config._fields).intersection(set(config)):
            del config[key]
        # set bravado config object
        config['bravado'] = bravado_config

        swagger_spec = Spec.from_dict(
            spec_dict, origin_url, http_client, config,
        )
        return cls(swagger_spec, also_return_response=bravado_config.also_return_response)

    def get_model(self, model_name):
        return self.swagger_spec.definitions[model_name]

    def _get_resource(self, item):
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
        return ResourceDecorator(resource, self.__also_return_response)

    def __repr__(self):
        return u"%s(%s)" % (self.__class__.__name__, self.swagger_spec.api_url)

    def __getattr__(self, item):
        return self._get_resource(item)

    def __dir__(self):
        return self.swagger_spec.resources.keys()


def inject_headers_for_remote_refs(request_callable, request_headers):
    """Inject request_headers only when the request is to retrieve the
    remote refs in the swagger spec (vs being a request for a service call).

    :param request_callable: method on http_client to make a http request
    :param request_headers: headers to inject when retrieving remote refs
    """
    def request_wrapper(request_params, *args, **kwargs):

        def is_remote_ref_request(request_kwargs):
            # operation is only present for service calls
            return request_kwargs.get('operation') is None

        if is_remote_ref_request(kwargs):
            request_params['headers'] = request_headers

        return request_callable(request_params, *args, **kwargs)

    return request_wrapper


class ResourceDecorator(object):
    """
    Wraps :class:`bravado_core.resource.Resource` so that accesses to contained
    operations can be instrumented.
    """

    def __init__(self, resource, also_return_response=False):
        """
        :type resource: :class:`bravado_core.resource.Resource`
        """
        self.also_return_response = also_return_response
        self.resource = resource

    def __getattr__(self, name):
        """
        :rtype: :class:`CallableOperation`
        """
        return CallableOperation(getattr(self.resource, name), self.also_return_response)

    def __dir__(self):
        """
        Exposes correct attrs on resource when tab completing in a REPL
        """
        return self.resource.__dir__()


class CallableOperation(object):
    """Wraps an operation to make it callable and provides a docstring. Calling
    the operation uses the configured http_client.

    :type operation: :class:`bravado_core.operation.Operation`
    """

    def __init__(self, operation, also_return_response=False):
        self.also_return_response = also_return_response
        self.operation = operation

    @docstring_property(__doc__)
    def __doc__(self):
        return create_operation_docstring(self.operation)

    def __getattr__(self, name):
        """Forward requests for attrs not found on this decorator to the
        delegate.
        """
        return getattr(self.operation, name)

    def __call__(self, **op_kwargs):
        """Invoke the actual HTTP request and return a future.

        :rtype: :class:`bravado.http_future.HTTPFuture`
        """
        log.debug(u'%s(%s)', self.operation.operation_id, op_kwargs)
        warn_for_deprecated_op(self.operation)

        # Get per-request config
        request_options = op_kwargs.pop('_request_options', {})
        request_config = RequestConfig(request_options, self.also_return_response)

        request_params = construct_request(
            self.operation, request_options, **op_kwargs)

        http_client = self.operation.swagger_spec.http_client

        return http_client.request(
            request_params,
            operation=self.operation,
            request_config=request_config,
        )


def construct_request(operation, request_options, **op_kwargs):
    """Construct the outgoing request dict.

    :type operation: :class:`bravado_core.operation.Operation`
    :param request_options: _request_options passed into the operation
        invocation.
    :param op_kwargs: parameter name/value pairs to passed to the
        invocation of the operation.

    :return: request in dict form
    """
    url = operation.swagger_spec.api_url.rstrip('/') + operation.path_name
    request = {
        'method': str(operation.http_method.upper()),
        'url': url,
        'params': {},  # filled in downstream
        'headers': request_options.get('headers', {}),
    }
    # Adds Accept header to request for msgpack response if specified
    if request_options.get('use_msgpack', False):
        request['headers']['Accept'] = 'application/msgpack'

    # Copy over optional request options
    for request_option in ('connect_timeout', 'timeout'):
        if request_option in request_options:
            request[request_option] = request_options[request_option]

    construct_params(operation, request, op_kwargs)

    return request


def construct_params(operation, request, op_kwargs):
    """Given the parameters passed to the operation invocation, validates and
    marshals the parameters into the provided request dict.

    :type operation: :class:`bravado_core.operation.Operation`
    :type request: dict
    :param op_kwargs: the kwargs passed to the operation invocation

    :raises: SwaggerMappingError on extra parameters or when a required
        parameter is not supplied.
    """
    current_params = operation.params.copy()
    for param_name, param_value in iteritems(op_kwargs):
        param = current_params.pop(param_name, None)
        if param is None:
            raise SwaggerMappingError(
                "{0} does not have parameter {1}"
                .format(operation.operation_id, param_name))
        marshal_param(param, param_value, request)

    # Check required params and non-required params with a 'default' value
    for remaining_param in itervalues(current_params):
        if remaining_param.location == 'header' and remaining_param.name in request['headers']:
            marshal_param(remaining_param, request['headers'][remaining_param.name], request)
        else:
            if remaining_param.required:
                raise SwaggerMappingError(
                    '{0} is a required parameter'.format(remaining_param.name))
            if not remaining_param.required and remaining_param.has_default():
                marshal_param(remaining_param, None, request)
