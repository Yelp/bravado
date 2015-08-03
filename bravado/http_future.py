# -*- coding: utf-8 -*-
from bravado.exception import HTTPError


class HttpFuture(object):
    """A future which inputs HTTP params"""

    def __init__(self, future, response_adapter, callback):
        """Kicks API call for Fido client

        :param future: future object
        :type future: :class: `concurrent.futures.Future`
        :param response_adapter: Adapter which exposes json(), status_code()
        :type response_adapter: :class: `bravado_core.response.IncomingResponse`
        :param callback: Function to be called on the response
        """
        self.future = future
        self.response_adapter = response_adapter
        self.response_callback = callback

    def result(self, timeout=None):
        """Blocking call to wait for API response

        :param timeout: Number of seconds to wait for a response. Defaults to
            None which means wait indefinitely.
        :type timeout: float
        :return: swagger response return value when given a callback or the
            http_response otherwise.
        """
        http_response = self.response_adapter(
            self.future.result(timeout=timeout))

        if self.response_callback:
            swagger_return_value = self.response_callback(http_response)
            raise_http_error_based_on_status(
                http_response, swagger_return_value)
            return swagger_return_value

        return http_response


def raise_http_error_based_on_status(http_response, swagger_return_value):
    """
    Mimic behavior of the swaggerpy 1.2 implementation for backwards
    compatibility. Raise an HTTPError when the http status indicates a client
    or server side error.

    :param http_response: :class:`IncomingResponse`
    :param swagger_return_value: The return value of a swagger response if it
        has one, None otherwise.
    :raises: HTTPError on 4XX and 5XX http errors
    """
    http_error_msg = None

    if 400 <= http_response.status_code < 500:
        http_error_msg = '{0} Client Error: {1}'.format(
            http_response.status_code, swagger_return_value)

    elif 500 <= http_response.status_code < 600:
        http_error_msg = '{0} Server Error: {1}'.format(
            http_response.status_code, swagger_return_value)

    if http_error_msg:
        raise HTTPError(http_error_msg, http_response, swagger_return_value)
