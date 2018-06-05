# -*- coding: utf-8 -*-
import monotonic
from bravado_core.content_type import APP_JSON
from bravado_core.response import IncomingResponse


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

    def __init__(self, incoming_response, swagger_result, start_time, request_end_time, handled_exception_info):
        """
        :param incoming_response: a subclass of bravado_core.response.IncomingResponse.
        :param swagger_result: the unmarshalled result that is being returned to the user.
        :param start_time: monotonic timestamp indicating when the HTTP future was created. Depending on the
            internal operation of the HTTP client used, this is either before the HTTP request was initiated
            (default client) or right after the HTTP request was sent (e.g. bravado-asyncio / fido).
        :param request_end_time: monotonic timestamp indicating when we received the incoming response,
            excluding unmarshalling, validation or potential fallback result processing.
        :param handled_exception_info: sys.exc_info() data if an exception was caught and handled as
            part of a fallback response; note that the third element in the list is a string representation
            of the traceback, not a traceback object.
        """
        self._incoming_response = incoming_response
        self.start_time = start_time
        self.request_end_time = request_end_time
        self.processing_end_time = monotonic.monotonic()
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

    @property
    def request_elapsed_time(self):
        return self.request_end_time - self.start_time

    @property
    def elapsed_time(self):
        return self.processing_end_time - self.start_time


class FallbackIncomingResponse(IncomingResponse):
    """An IncomingResponse implementation that contains a fallback result to be returned; we're using it
    so that we can unmarshal (and potentially validate) the response the user provided."""

    def __init__(self, result, status_code=200):
        self._result = result
        self.status_code = status_code

    @property
    def headers(self):
        return {'content-type': APP_JSON}

    def json(self):
        return self._result
