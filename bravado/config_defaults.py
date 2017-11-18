# -*- coding: utf-8 -*-
CONFIG_DEFAULTS = {
    # See the constructor of :class:`bravado.http_future.HttpFuture` for an
    # in depth explanation of what this means.
    'also_return_response': False,
}

REQUEST_OPTIONS_DEFAULTS = {
    # List of callbacks that are executed after the incoming response has been
    # validated and the swagger_result has been unmarshalled.
    #
    # The callback should expect two arguments:
    #   param : incoming_response
    #   type  : subclass of class:`bravado_core.response.IncomingResponse`
    #   param : operation
    #   type  : class:`bravado_core.operation.Operation`
    'response_callbacks': [],
}
