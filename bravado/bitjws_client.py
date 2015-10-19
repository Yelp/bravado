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
import functools
import logging
import sys

from bravado_core.docstring import create_operation_docstring
from bravado_core.exception import MatchingResponseNotFound
from bravado_core.exception import SwaggerMappingError
from bravado_core.formatter import SwaggerFormat  # noqa
from bravado_core.param import marshal_param
from bravado_core.response import unmarshal_response
from bravado_core.spec import Spec
import six
from six import iteritems, itervalues

from bravado.docstring_property import docstring_property
from bravado.exception import HTTPError
from bravado.requests_client import RequestsClient
from bravado.swagger_model import Loader
from bravado.warning import warn_for_deprecated_op

from bravado.client import *

import bitjws

log = logging.getLogger(__name__)


class BitJWSResourceDecorator(object):
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
        return BitJWSCallableOperation(getattr(self.resource, name))

    def __dir__(self):
        """
        Exposes correct attrs on resource when tab completing in a REPL
        """
        return self.resource.__dir__()


class BitJWSCallableOperation(object):
    """
    Wraps an operation to make it callable and provide a docstring. Calling
    the operation uses the configured http_client.
    """
    def __init__(self, operation):
        """
        :type operation: :class:`bravado_core.operation.Operation`
        """
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
        callback = functools.partial(bitjws_response_callback, operation=self)
        return self.operation.swagger_spec.http_client.request(request_params,
                                                               callback)


def bitjws_response_callback(incoming_response, operation):
    """
    So the http_client is finished with its part of processing the response.
    This hands the response over to bravado_core for validation and
    unmarshalling.

    :type incoming_response: :class:`bravado_core.response.IncomingResponse`
    :type operation: :class:`bravado_core.operation.Operation`
    :return: Response spec's return value.
    :raises: HTTPError
        - On 5XX status code, the HTTPError has minimal information.
        - On non-2XX status code with no matching response, the HTTPError
            contains a detailed error message.
        - On non-2XX status code with a matching response, the HTTPError
            contains the return value.
    """
    raise_on_unexpected(incoming_response)

    print incoming_response.text
    print incoming_response._delegate.content.decode('utf8')
    try:
        swagger_return_value = unmarshal_response(incoming_response, operation)
    except MatchingResponseNotFound as e:
        six.reraise(
            HTTPError,
            HTTPError(response=incoming_response, message=str(e)),
            sys.exc_info()[2])

    raise_on_expected(incoming_response, swagger_return_value)
    return swagger_return_value

