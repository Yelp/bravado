# -*- coding: utf-8 -*-
import inspect

import mock
import pytest

from bravado.exception import HTTPServerError
from bravado.http_future import HttpFuture
from bravado.response import BravadoResponseMetadata
from bravado.testing.response_mocks import BravadoResponseMock
from bravado.testing.response_mocks import DegradedBravadoResponseMock
from bravado.testing.response_mocks import make_bravado_response


@pytest.fixture
def mock_result():
    return mock.Mock(name='mock result')


def test_response_mock_signatures():
    """Make sure the mocks' __call__ methods have the same signature as HttpFuture.response"""
    response_signature = inspect.getargspec(HttpFuture.response)

    assert inspect.getargspec(BravadoResponseMock.__call__) == response_signature
    assert inspect.getargspec(DegradedBravadoResponseMock.__call__) == response_signature


@pytest.mark.parametrize(
    'is_degraded, expected_class',
    (
        (False, BravadoResponseMock),
        (True, DegradedBravadoResponseMock)
    )
)
def test_make_bravado_response(is_degraded, expected_class, mock_result):
    response = make_bravado_response(mock_result, degraded=is_degraded)

    assert isinstance(response, expected_class)


def test_bravado_response(mock_result):
    response_mock = BravadoResponseMock(mock_result)
    response = response_mock()

    assert response.result is mock_result
    assert isinstance(response.metadata, BravadoResponseMetadata)
    assert response.metadata._swagger_result is mock_result


def test_degraded_bravado_response(mock_result):
    exception = HTTPServerError(mock.Mock('incoming response', status_code=500))

    def handle_fallback_result(exc):
        assert exc is exception
        return mock_result

    response_mock = DegradedBravadoResponseMock(exception)
    response = response_mock(fallback_result=handle_fallback_result)

    assert response.result is mock_result
    assert isinstance(response.metadata, BravadoResponseMetadata)
    assert response.metadata._swagger_result is mock_result
