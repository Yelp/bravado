# -*- coding: utf-8 -*-
import logging

from bravado.config import _import_class

log = logging.getLogger(__name__)


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
        self._incoming_response = incoming_response
        self.elapsed_time = elapsed_time
        self.exc_info = exc_info

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
        return self.exc_info is not None


def get_metadata_class(fully_qualified_class_str):
    class_to_import = _import_class(fully_qualified_class_str)
    if not class_to_import:
        return BravadoResponseMetadata

    if issubclass(class_to_import, BravadoResponseMetadata):
        return class_to_import

    log.warning(
        'bravado configuration error: the metadata class {fully_qualified_class_str}\' does not extend '
        'BravadoResponseMetadata. Using default class instead.'.format(
            fully_qualified_class_str=fully_qualified_class_str,
        )
    )
    return BravadoResponseMetadata
