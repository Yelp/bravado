# -*- coding: utf-8 -*-


class BravadoResponse(object):
    """Bravado response object containing the swagger result as well as response metadata.

    WARNING: This interface is considered UNSTABLE. Backwards-incompatible API changes may occur;
    use at your own risk.
    """

    def __init__(self, result, metadata):
        self.result = result
        self.metadata = metadata

    @property
    def incoming_response(self):
        return self.metadata.incoming_response


class BravadoResponseMetadata(object):
    """HTTP response metadata.

    NOTE: The `elapsed_time` attribute might be slightly lower than the actual time spent since calling
    the operation object, as we only start measuring once the call to `HTTPClient.request` returns.
    Nevertheless, it should be accurate enough for logging and debugging, i.e. determining what went
    on and how much time was spent waiting for the response.

    WARNING: This interface is considered UNSTABLE. Backwards-incompatible API changes may occur;
    use at your own risk.
    """

    def __init__(self, incoming_response, swagger_result, elapsed_time, handled_exception_info):
        """
        :param incoming_response: a subclass of bravado_core.response.IncomingResponse.
        :param swagger_result: the unmarshalled result that is being returned to the user.
        :param elapsed_time: float containing an approximate elapsed time since creating the future, in seconds.
        :param handled_exception_info: sys.exc_info() data if an exception was caught and handled as
            part of a fallback response; note that the third element in the list is a string representation
            of the traceback, not a traceback object.
        """
        self._incoming_response = incoming_response
        self.elapsed_time = elapsed_time
        self.handled_exception_info = handled_exception_info

        # we expose the result to the user through the BravadoResponse object;
        # we're passing it in to this object in case custom implementations need it
        self._swagger_result = swagger_result

    @property
    def incoming_response(self):
        if not self._incoming_response:
            raise ValueError('No incoming_response present')
        return self._incoming_response

    @property
    def status_code(self):
        return self.incoming_response.status_code

    @property
    def headers(self):
        return self.incoming_response.headers

    @property
    def is_fallback_result(self):
        return self.handled_exception_info is not None
