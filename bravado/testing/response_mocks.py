# -*- coding: utf-8 -*-
import mock

from bravado.exception import BravadoTimeoutError
from bravado.http_future import FALLBACK_EXCEPTIONS
from bravado.response import BravadoResponseMetadata


class BravadoResponseMock(object):
    """Class that behaves like the :meth:`.HttpFuture.response` method as well as a :class:`.BravadoResponse`.
    Please check the documentation for further information.
    """

    def __init__(self, result, metadata=None):
        self._result = result
        if metadata:
            self._metadata = metadata
        else:
            self._metadata = BravadoResponseMetadata(
                incoming_response=mock.Mock(
                    status_code=200,
                    headers={},
                ),
                swagger_result=self._result,
                start_time=1528733800,
                request_end_time=1528733801,
                handled_exception_info=None,
                request_config=None,
            )

    def __call__(self, timeout=None, fallback_result=None, exceptions_to_catch=FALLBACK_EXCEPTIONS):
        return self

    @property
    def result(self):
        return self._result

    @property
    def metadata(self):
        return self._metadata


class FallbackResultBravadoResponseMock(object):
    """Class that behaves like the :meth:`.HttpFuture.response` method as well as a :class:`.BravadoResponse`.
    It will always call the ``fallback_result`` callback that's passed to the ``response()`` method.
    Please check the documentation for further information.
    """

    def __init__(self, exception=BravadoTimeoutError(), metadata=None):
        self._exception = exception
        if metadata:
            self._metadata = metadata
        else:
            self._metadata = BravadoResponseMetadata(
                incoming_response=None,
                swagger_result=None,  # we're going to set it later
                start_time=1528733800,
                request_end_time=1528733801,
                handled_exception_info=(self._exception.__class__, self._exception, 'Traceback'),
                request_config=None,
            )

    def __call__(self, timeout=None, fallback_result=None, exceptions_to_catch=FALLBACK_EXCEPTIONS):
        self._fallback_result = fallback_result(self._exception)
        self._metadata._swagger_result = self._fallback_result
        return self

    @property
    def result(self):
        return self._fallback_result

    @property
    def metadata(self):
        return self._metadata
