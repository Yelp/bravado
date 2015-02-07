import logging

from yelp_uri import urllib_utf8

from bravado import swagger_type
from bravado.mapping.param import validate_and_add_params_to_request
from bravado.response import post_receive, HTTPFuture
from bravado.exception import SwaggerError

log = logging.getLogger(__name__)


# TOOD: swagger_type.get_swagger_type() is called so many times (across this
#       module and param.py. Refactor state in Param class

class Operation(object):
    """Perform a request by taking the kwargs passed to the call and
    constructing an HTTP request.
    """
    def __init__(self, spec, path_name, http_method, operation_spec):
        self.spec = spec
        self.path_name = path_name
        self.http_method = http_method
        self.operation_spec = operation_spec
        self._operation_id = None  # use @property getter

    @property
    def operation_id(self):
        """A friendly name for the operation. The id MUST be unique among all
        operations described in the API. Tools and libraries MAY use the
        operation id to uniquely identify an operation.

        This this field is not required, it will be generated when needed.

        :rtype: str
        """
        if self._operation_id is None:
            self._operation_id = self.operation_spec.get('operationId')
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

        for param_spec in self.operation_spec.get('parameters', []):
            param_name = param_spec['name']
            param_location = param_spec['in']
            param_value = kwargs.pop(param_name, None)
            param_default = param_spec.get('default')

            # if param_location == 'body':
            #     spec_for_param = param_spec['schema']
            # else:
            #     spec_for_param = param_spec

            # This is really convoluted! Given a paramever spec like so, the
            # type is "array" but the default value is the string "available".
            # Since when is a string an array?!?! The code special cases
            # array types with a default value and wraps the value in an
            # array for convenience.
            #
            # {
            #     name: "status",
            #     in: "query",
            #     description: "Status values that need to be considered for filter",
            #     required: false,
            #     type: "array",
            #     items: {
            #         type: "string"
            #     },
            #     collectionFormat: "multi",
            #     default: "available"
            # }
            #
            # Snippet from http://petstore.swagger.wordnik.com/v2/swagger.json
            # TODO: Unit test
            if param_value is None and param_default:
                param_type = param_spec['type']
                if param_type == 'array':
                    param_value = [param_default]
                else:
                    param_value = param_default

            validate_and_add_params_to_request(
                self.spec,
                param_spec,
                param_value,
                request)

        if kwargs:
            raise TypeError(u"{0} does not have parameters {1}".format(
                self.operation_id, kwargs.keys()))
        return request

    def __call__(self, **kwargs):
        log.debug(u"%s(%s)" % (self.operation_id, kwargs))
        request = self._construct_request(**kwargs)

        def response_future(response, **kwargs):
            # Assume status is OK, an exception would have been raised already
            if not response.text:
                return None

            status_code = str(response.status_code)
            # Handle which repsonse to activate given status_code
            default_response_spec = self.operation_spec['responses'].get('default', None)
            response_spec = self.operation_spec['responses'].get(status_code, default_response_spec)
            if response_spec is None:
                # reponse code doesn't match and no default provided
                if status_code == '200':
                    # it was obviously successful
                    log.warn("Op {0} was successful by didn't match any responses".format(self.operation_id))
                else:
                    raise SwaggerError("Response doesn't match any expected responses: {0}".format(response))

            response_dict = response.json()

            if response_spec and 'schema' in response_spec:
                swagger_type_ = swagger_type.get_swagger_type(response_spec['schema'])
            else:
                swagger_type_ = None

            log.debug('response_dict = %s' % response_dict)
            log.debug('response_spec = %s' % response_spec)
            log.debug('swagger_type  = %s' % swagger_type_)

            return post_receive(
                response_dict,
                swagger_type_,
                self.spec.definitions,
                **kwargs)

        return HTTPFuture(self.spec.http_client, request, response_future)
