from functools import partial
import logging

from yelp_uri import urllib_utf8

from bravado import swagger_type
from bravado.mapping.docstring import create_operation_docstring, \
    docstring_property
from bravado.mapping.param import validate_and_add_params_to_request
from bravado.response import post_receive, HTTPFuture

log = logging.getLogger(__name__)


# TOOD: swagger_type.get_swagger_type() is called so many times (across this
#       module and param.py. Refactor state in Param class

class Operation(object):
    """Perform a request by taking the kwargs passed to the call and
    constructing an HTTP request.
    """
    def __init__(self, spec, path_name, http_method, operation_dict):
        self.spec = spec
        self.path_name = path_name
        self.http_method = http_method
        self.operation_dict = operation_dict
        self._operation_id = None  # use @property getter
        # lazy docstring
        self.__doc__ = docstring_property(
            partial(create_operation_docstring, self))

    @property
    def operation_id(self):
        """A friendly name for the operation. The id MUST be unique among all
        operations described in the API. Tools and libraries MAY use the
        operation id to uniquely identify an operation.

        This this field is not required, it will be generated when needed.

        :rtype: str
        """
        if self._operation_id is None:
            self._operation_id = self.operation_dict.get('operationId')
            if self._operation_id is None:
                # build based on the http method and request path
                self._operation_id = (self.http_method + '_' + self.path_name)\
                    .replace('/', '_')\
                    .replace('{', '_')\
                    .replace('}', '_')\
                    .replace('__', '_')\
                    .strip('_')
        return self._operation_id

    def __repr__(self):
        return u"%s(%s)" % (self.__class__.__name__, self.operation_id)

    def _construct_request(self, **kwargs):
        """
        :param kwargs: parameter name/value pairs to pass to the invocation of
            the operation
        :return: request in dict form
        """
        request_options = kwargs.pop('_request_options', {})

        request = {}
        request['method'] = self.http_method
        request['url'] = self.spec.api_url + self.path_name
        request['params'] = {}
        request['headers'] = request_options.get('headers', {})

        for param_dict in self.operation_dict.get('parameters', []):
            param_name = param_dict['name']
            param_value = kwargs.pop(param_name, param_dict.get('default'))
            validate_and_add_params_to_request(
                self.spec,
                param_dict,
                param_value,
                request)

        if kwargs:
            raise TypeError(u"{0} does not have parameters {1}".format(
                self.operation_id, kwargs.keys()))
        return request

    def __call__(self, **kwargs):
        log.debug(u"%s?%r" % (self.operation_id, urllib_utf8.urlencode(kwargs)))
        request = self._construct_request(**kwargs)

        def response_future(response, **kwargs):
            # Assume status is OK, an exception would have been raised already
            if not response.text:
                return None

            print response.json()

            return post_receive(
                response.json(),
                swagger_type.get_swagger_type(self.operation_dict),
                self.spec.definitions,
                **kwargs)

        return HTTPFuture(self.spec.http_client, request, response_future)
