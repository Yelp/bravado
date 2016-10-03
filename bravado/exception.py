# -*- coding: utf-8 -*-
from six import with_metaclass


# Dictionary of HTTP status codes to exception classes
status_map = {}


def _register_exception(exception_class):
    """Store an HTTP exception class with a status code into a mapping
    of status codes to exception classes.
    :param exception_class: A subclass of HTTPError
    :type exception_class: :class:`HTTPError`
    """
    status_map[exception_class.status_code] = exception_class


class HTTPErrorType(type):
    """A metaclass for registering HTTPError subclasses."""

    def __new__(cls, *args, **kwargs):
        new_class = super(HTTPErrorType, cls).__new__(cls, *args, **kwargs)
        if hasattr(new_class, 'status_code'):
            _register_exception(new_class)
        return new_class


class HTTPError(with_metaclass(HTTPErrorType, IOError)):
    """Unified HTTPError used across all http_client implementations.
    """

    def __init__(self, response, message=None, swagger_result=None):
        """
        :type response: :class:`bravado_core.response.IncomingResponse`
        :param message: Optional string message
        :param swagger_result: If the response for this HTTPError is
            documented in the swagger spec, then this should be the result
            value of the response.
        """
        self.response = response
        self.message = message
        self.swagger_result = swagger_result
        self.status_code = self.response.status_code

    def __str__(self):
        # Try to surface the most useful/relevant information available
        # since this is the first thing a developer sees when bad things
        # happen.
        status_and_reason = str(self.response)
        message = ': ' + self.message if self.message else ''
        result = ': {0}'.format(self.swagger_result) \
            if self.swagger_result is not None else ''
        return '{0}{1}{2}'.format(status_and_reason, message, result)


def make_http_exception(response, message=None, swagger_result=None):
    """
    Return an HTTP exception class  based on the response. If a specific
    class doesn't exist for a particular HTTP status code, a more
    general :class:`HTTPError` class will be returned.
    :type response: :class:`bravado_core.response.IncomingResponse`
    :param message: Optional string message
    :param swagger_result: If the response for this HTTPError is
        documented in the swagger spec, then this should be the result
        value of the response.
    :return: An HTTP exception class that can be raised
    """
    exc_class = status_map.get(response.status_code, HTTPError)
    return exc_class(response, message=message, swagger_result=swagger_result)


class HTTPClientError(HTTPError):
    """4xx responses."""


class HTTPServerError(HTTPError):
    """5xx responses."""


# The follow are based on the HTTP Status Code Registry at
# http://www.iana.org/assignments/http-status-codes/http-status-codes.xhtml

class HTTPBadRequest(HTTPClientError):
    status_code = 400


class HTTPUnauthorized(HTTPClientError):
    status_code = 401


class HTTPPaymentRequired(HTTPClientError):
    status_code = 402


class HTTPForbidden(HTTPClientError):
    status_code = 403


class HTTPNotFound(HTTPClientError):
    status_code = 404


class HTTPMethodNotAllowed(HTTPClientError):
    status_code = 405


class HTTPNotAcceptable(HTTPClientError):
    status_code = 406


class HTTPProxyAuthenticationRequired(HTTPClientError):
    status_code = 407


class HTTPRequestTimeout(HTTPClientError):
    status_code = 408


class HTTPConflict(HTTPClientError):
    status_code = 409


class HTTPGone(HTTPClientError):
    status_code = 410


class HTTPLengthRequired(HTTPClientError):
    status_code = 411


class HTTPPreconditionFailed(HTTPClientError):
    status_code = 412


class HTTPPayloadTooLarge(HTTPClientError):
    status_code = 413


class HTTPURITooLong(HTTPClientError):
    status_code = 414


class HTTPUnsupportedMediaType(HTTPClientError):
    status_code = 415


class HTTPRangeNotSatisfiable(HTTPClientError):
    status_code = 416


class HTTPExpectationFailed(HTTPClientError):
    status_code = 417


class HTTPMisdirectedRequest(HTTPClientError):
    status_code = 421


class HTTPUnprocessableEntity(HTTPClientError):
    status_code = 422


class HTTPLocked(HTTPClientError):
    status_code = 423


class HTTPFailedDependency(HTTPClientError):
    status_code = 424


class HTTPUpgradeRequired(HTTPClientError):
    status_code = 426


class HTTPPreconditionRequired(HTTPClientError):
    status_code = 428


class HTTPTooManyRequests(HTTPClientError):
    status_code = 429


class HTTPRequestHeaderFieldsTooLarge(HTTPClientError):
    status_code = 431


class HTTPUnavailableForLegalReasons(HTTPClientError):
    status_code = 451


class HTTPInternalServerError(HTTPServerError):
    status_code = 500


class HTTPNotImplemented(HTTPServerError):
    status_code = 501


class HTTPBadGateway(HTTPServerError):
    status_code = 502


class HTTPServiceUnavailable(HTTPServerError):
    status_code = 503


class HTTPGatewayTimeout(HTTPServerError):
    status_code = 504


class HTTPHTTPVersionNotSupported(HTTPServerError):
    status_code = 505


class HTTPVariantAlsoNegotiates(HTTPServerError):
    status_code = 506


class HTTPInsufficientStorage(HTTPServerError):
    status_code = 507


class HTTPLoopDetected(HTTPServerError):
    status_code = 508


class HTTPNotExtended(HTTPServerError):
    status_code = 510


class HTTPNetworkAuthenticationRequired(HTTPServerError):
    status_code = 511
