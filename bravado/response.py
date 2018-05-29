# -*- coding: utf-8 -*-


class BravadoResponse(object):
    """Bravado response object containing the swagger result as well as response metadata.

    WARNING: This interface is considered UNSTABLE. Backwards-incompatible API changes may occur;
    use at your own risk.
    """

    def __init__(self, result, response_metadata):
        self.result = result
        self.response_metadata = response_metadata

    @property
    def incoming_response(self):
        return self.response_metadata.incoming_response


class BravadoResponseMetadata(object):
    """HTTP response metadata.

    NOTE: The `elapsed_time` attribute might be slightly lower than the actual time spent since calling
    the operation object, as we only start measuring once the call to `HTTPClient.request` returns.
    Nevertheless, it should be accurate enough for logging and debugging, i.e. determining what went
    on and how much time was spent waiting for the response.

    WARNING: This interface is considered UNSTABLE. Backwards-incompatible API changes may occur;
    use at your own risk.
    """

    def __init__(self, incoming_response, swagger_result, elapsed_time, exc_info):
        self.incoming_response = incoming_response
        self.elapsed_time = elapsed_time
        self.exc_info = exc_info

        # we expose the result to the user through the BravadoResponse object;
        # we're passing it in to this object in case custom implementations need it
        self._swagger_result = swagger_result

    @property
    def status_code(self):
        if not self.incoming_response:
            raise ValueError('No incoming_response present')

        return self.incoming_response.status_code

    @property
    def headers(self):
        if not self.incoming_response:
            raise ValueError('No incoming_response present')

        return self.incoming_response.headers

    @property
    def is_fallback_result(self):
        return self.exc_info is not None
