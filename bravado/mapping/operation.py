from yelp_uri import urllib_utf8

#from bravado.client import validate_and_add_params_to_request, log
from bravado.mapping.docstring import create_operation_docstring

from response import post_receive, HTTPFuture


class Operation(object):
    """Perform a request by taking the kwargs passed to the call and
    constructing an HTTP request.
    """

    def __init__(self, uri, operation, http_client, models):
        self._uri = uri
        self._json = operation
        self._http_client = http_client
        self._models = models
        self.__doc__ = create_operation_docstring(operation)

    def __repr__(self):
        return u"%s(%s)" % (self.__class__.__name__, self._json[u'nickname'])

    def _construct_request(self, **kwargs):
        _request_options = kwargs.pop('_request_options', {}) or {}

        request = {}
        request['method'] = self._json[u'method']
        request['url'] = self._uri
        request['params'] = {}
        request['headers'] = _request_options.get('headers', {}) or {}

        for param in self._json.get(u'parameters', []):
            value = kwargs.pop(param[u'name'], param.get('defaultValue'))
            validate_and_add_params_to_request(param, value, request,
                                               self._models)
        if kwargs:
            raise TypeError(u"'%s' does not have parameters %r" % (
                self._json[u'nickname'], kwargs.keys()))
        return request

    def __call__(self, **kwargs):
        log.debug(u"%s?%r" % (
            self._json[u'nickname'],
            urllib_utf8.urlencode(kwargs)))
        request = self._construct_request(**kwargs)

        def response_future(response, **kwargs):
            # Assume status is OK, an exception would have been raised already
            if not response.text:
                return None

            return post_receive(
                response.json(),
                swagger_type.get_swagger_type(self._json),
                self._models,
                **kwargs)
        return HTTPFuture(self._http_client, request, response_future)