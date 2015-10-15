# -*- coding: utf-8 -*-
APP_FORM = 'application/x-www-form-urlencoded'
MULT_FORM = 'multipart/form-data'


class HttpClient(object):
    """Interface for a minimal HTTP client.
    """
    def request(self, request_params, response_callback=None,
                also_return_response=False):
        """
        :param request_params: complete request data. e.g. url, method,
            headers, body, params, connect_timeout, timeout, etc.
        :type request_params: dict
        :param response_callback: Function to be called on response
        :type response_callback: method
        :param also_return_response: Consult the constructor documentation for
            :class:`bravado.http_future.HttpFuture`.

        :returns: HTTP Future object
        :rtype: :class: `bravado_core.http_future.HttpFuture`
        """
        raise NotImplementedError(
            u"%s: Method not implemented", self.__class__.__name__)

    def __repr__(self):
        return "{0}()".format(type(self))
