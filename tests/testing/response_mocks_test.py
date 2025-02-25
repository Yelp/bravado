# -*- coding: utf-8 -*-
try:
    from inspect import getfullargspec as getargspec
except ImportError:
    from inspect import getargspec

import mock
import pytest
from bravado_core.response import IncomingResponse

from bravado.config import RequestConfig
from bravado.exception import HTTPServerError
from bravado.http_future import HttpFuture
from bravado.response import BravadoResponseMetadata
from bravado.testing.response_mocks import BravadoResponseMock
from bravado.testing.response_mocks import FallbackResultBravadoResponseMock


@pytest.fixture
def mock_result():
    return mock.NonCallableMock(name='mock result')


@pytest.fixture
def mock_metadata():
    return BravadoResponseMetadata(
        incoming_response=IncomingResponse(),
        swagger_result=None,
        start_time=5,
        request_end_time=6,
        handled_exception_info=None,
        request_config=RequestConfig({}, also_return_response_default=False),
    )


def test_response_mock_signatures():
    """Make sure the mocks' __call__ methods have the same signature as HttpFuture.response"""
    response_signature = getargspec(HttpFuture.response)

    assert getargspec(BravadoResponseMock.__call__) == response_signature
    assert getargspec(FallbackResultBravadoResponseMock.__call__) == response_signature


def test_bravado_response(mock_result):
    response_mock = BravadoResponseMock(mock_result)
    response = response_mock()

    assert response.result is mock_result
    assert isinstance(response.metadata, BravadoResponseMetadata)
    assert response.metadata._swagger_result is mock_result


def test_bravado_response_custom_metadata(mock_result, mock_metadata):
    response_mock = BravadoResponseMock(mock_result, metadata=mock_metadata)
    response = response_mock()

    assert response.metadata is mock_metadata


def test_fallback_result_bravado_response(mock_result):
    # type: (mock.NonCallableMagicMock) -> None
    response_mock = FallbackResultBravadoResponseMock()
    response = response_mock(fallback_result=mock_result)

    assert response.result is mock_result
    assert isinstance(response.metadata, BravadoResponseMetadata)
    assert response.metadata._swagger_result is mock_result


def test_fallback_result_bravado_response_callable(mock_result):
    exception = HTTPServerError(mock.Mock('incoming response', status_code=500))

    def handle_fallback_result(exc):
        assert exc is exception
        return mock_result

    response_mock = FallbackResultBravadoResponseMock(exception)
    response = response_mock(fallback_result=handle_fallback_result)

    assert response.result is mock_result
    assert isinstance(response.metadata, BravadoResponseMetadata)
    assert response.metadata._swagger_result is mock_result


def test_fallback_result_bravado_response_custom_metadata(mock_result, mock_metadata):
    response_mock = FallbackResultBravadoResponseMock(metadata=mock_metadata)
    response = response_mock(fallback_result=mock_result)

    assert response.metadata is mock_metadata
    assert response.metadata._swagger_result is mock_result


def test_fallback_result_response_without_fallback_result():
    response_mock = FallbackResultBravadoResponseMock()
    with pytest.raises(AssertionError):
        response_mock()
