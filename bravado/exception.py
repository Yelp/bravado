# -*- coding: utf-8 -*-


class HTTPError(IOError):
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

    def __str__(self):
        # Try to surface the most useful/relevant information available
        # since this is the first thing a developer sees when bad things
        # happen.
        status_and_reason = str(self.response)
        message = ': ' + self.message if self.message else ''
        result = ': {0}'.format(self.swagger_result) \
            if self.swagger_result is not None else ''
        return '{0}{1}{2}'.format(status_and_reason, message, result)
