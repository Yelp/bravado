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
    :param return_swagger_result: returns the Swagger result
        when True or the HTTP response object when False. This is useful
        if you want access to additional data from the HTTP response other than
        just the Swagger result. e.g. http headers, http response code, etc.
        Defaults to true mostly for backwards compatibility and simplicity at
        the Swagger client's call site.
    """
    def __init__(self, future, response_adapter, callback,
                 return_swagger_result=True):
        self.future = future
        self.response_adapter = response_adapter
        self.response_callback = callback
        self.return_swagger_result = return_swagger_result

    def result(self, timeout=None):
        """Blocking call to wait for the HTTP response.

        :param timeout: Number of seconds to wait for a response. Defaults to
            None which means wait indefinitely.
        :type timeout: float
        :return: Depends on the value of return_swagger_result sent in
            to the constructor.
        """
        inner_response = self.future.result(timeout=timeout)
        incoming_response = self.response_adapter(inner_response)

        if self.response_callback:
            self.response_callback(incoming_response)
            if self.return_swagger_result:
                return incoming_response.swagger_result
            return incoming_response

        if 200 <= incoming_response.status_code < 300:
            return incoming_response

        raise HTTPError(response=incoming_response)
