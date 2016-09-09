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
        self.status_code = getattr(self.response, 'status_code')

    def __str__(self):
        # Try to surface the most useful/relevant information available
        # since this is the first thing a developer sees when bad things
        # happen.
        status_and_reason = str(self.response)
        message = ': ' + self.message if self.message else ''
        result = ': {0}'.format(self.swagger_result) \
            if self.swagger_result is not None else ''
        return '{0}{1}{2}'.format(status_and_reason, message, result)


class HTTPClientError(HTTPError):
    """4xx responses."""


class HTTPBadRequest(HTTPClientError):
    status_code = 400


class HTTPUnauthorized(HTTPClientError):
    status_code = 401


class HTTPForbidden(HTTPClientError):
    status_code = 403


class HTTPNotFound(HTTPClientError):
    status_code = 404


class HTTPServerError(HTTPError):
    """5xx responses."""


class HTTPInternalServerError(HTTPServerError):
    status_code = 500


class HTTPBadGateway(HTTPServerError):
    status_code = 503


class HTTPGatewayTimeout(HTTPServerError):
    status_code = 504


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
