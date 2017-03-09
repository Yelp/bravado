# -*- coding: utf-8 -*-
APP_FORM = 'application/x-www-form-urlencoded'
MULT_FORM = 'multipart/form-data'


class HttpClient(object):
    """Interface for a minimal HTTP client that can retrieve Swagger specs
    and perform HTTP calls to fulfill a Swagger operation.
    """

    def request(self, request_params, operation=None, response_callbacks=None,
                also_return_response=False):
        """
        :param request_params: complete request data. e.g. url, method,
            headers, body, params, connect_timeout, timeout, etc.
        :type request_params: dict
        :param operation: operation that this http request is for. Defaults
            to None - in which case, we're obviously just retrieving a Swagger
            Spec.
        :type operation: :class:`bravado_core.operation.Operation`
        :param response_callbacks: List of callables to post-process the
            incoming response. Expects args incoming_response and operation.
        :param also_return_response: Consult the constructor documentation for
            :class:`bravado.http_future.HttpFuture`.

        :returns: HTTP Future object
        :rtype: :class: `bravado_core.http_future.HttpFuture`
        """
        raise NotImplementedError(
            u"%s: Method not implemented", self.__class__.__name__)

    def __repr__(self):
        return "{0}()".format(type(self))
