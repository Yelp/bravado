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
        inner_response = self.future.result(timeout=timeout)
        incoming_response = self.response_adapter(inner_response)

        if self.response_callback:
            swagger_return_value = self.response_callback(incoming_response)
            return swagger_return_value

        if 200 <= incoming_response.status_code < 300:
            return incoming_response

        raise HTTPError(response=incoming_response)
