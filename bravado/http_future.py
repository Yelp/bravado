# -*- coding: utf-8 -*-
from bravado.exception import HTTPError


class HttpFuture(object):
    """Wrapper for a :class:`concurrent.futures.Future` that returns an HTTP
    response.

    :param future: The concurrent future to wrap.
    :type future: :class: `concurrent.futures.Future`
    :param response_adapter: Adapter type which exposes the innards of the HTTP
        response in a non-http client specific way.
    :type response_adapter: type that is a subclass of
        :class:`bravado_core.response.IncomingResponse`.
    :param callback: Function to be called on the response (usually for
        bravado-core post-processing).
    :param also_return_response: Determines if the incoming http response is
        included as part of the return value from calling
        `HttpFuture.result()`.
        When False, only the swagger result is returned.
        When True, the tuple(swagger result, http response) is returned.
        This is useful if you want access to additional data that is not
        accessible from the swagger result. e.g. http headers,
        http response code, etc.
        Defaults to False for backwards compatibility.
    """
    def __init__(self, future, response_adapter, callback,
                 also_return_response=False):
        self.future = future
        self.response_adapter = response_adapter
        self.response_callback = callback
        self.also_return_response = also_return_response

    def result(self, timeout=None):
        """Blocking call to wait for the HTTP response.

        :param timeout: Number of seconds to wait for a response. Defaults to
            None which means wait indefinitely.
        :type timeout: float
        :return: Depends on the value of also_return_response sent in
            to the constructor.
        """
        inner_response = self.future.result(timeout=timeout)
        incoming_response = self.response_adapter(inner_response)

        if self.response_callback:
            self.response_callback(incoming_response)
            swagger_result = incoming_response.swagger_result
            if self.also_return_response:
                return swagger_result, incoming_response
            return swagger_result

        if 200 <= incoming_response.status_code < 300:
            return incoming_response

        raise HTTPError(response=incoming_response)
