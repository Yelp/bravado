# -*- coding: utf-8 -*-
from bravado.exception import BravadoTimeoutError
from bravado.http_future import FALLBACK_EXCEPTIONS
from bravado.response import BravadoResponseMetadata


class BravadoResponseMock(object):
    def __init__(self, result):
        self._result = result

    def __call__(self, timeout=None, fallback_result=None, exceptions_to_catch=FALLBACK_EXCEPTIONS):
        return self

    @property
    def result(self):
        return self._result

    @property
    def metadata(self):
        return BravadoResponseMetadata(
            incoming_response='incoming response',
            swagger_result=self._result,
            start_time=1528733800,
            request_end_time=1528733801,
            handled_exception_info=None,
            request_config=None,
        )


class DegradedBravadoResponseMock(object):
    def __init__(self, exception=BravadoTimeoutError()):
        self._exception = exception

    def __call__(self, timeout=None, fallback_result=None, exceptions_to_catch=FALLBACK_EXCEPTIONS):
        self._fallback_result = fallback_result(self._exception)
        return self

    @property
    def result(self):
        return self._fallback_result

    @property
    def metadata(self):
        return BravadoResponseMetadata(
            incoming_response=None,
            swagger_result=self._fallback_result,
            start_time=1528733800,
            request_end_time=1528733801,
            handled_exception_info=(self._exception.__class__, self._exception, 'Traceback'),
            request_config=None,
        )


def make_bravado_response(result, degraded=False):
    if degraded:
        return DegradedBravadoResponseMock()
    else:
        return BravadoResponseMock(result)
