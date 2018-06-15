# -*- coding: utf-8 -*-
import mock
import pytest
from bravado_core.response import IncomingResponse

from bravado.config import BravadoConfig
from bravado.config import RequestConfig
from bravado.exception import BravadoTimeoutError
from bravado.exception import ForcedFallbackResultError
from bravado.exception import HTTPInternalServerError
from bravado.http_future import HttpFuture
from bravado.response import BravadoResponseMetadata


class ResponseMetadata(BravadoResponseMetadata):
    pass


@pytest.fixture
def mock_incoming_response():
    return mock.Mock(spec=IncomingResponse, status_code=200, swagger_result=mock.Mock(name='swagger_result'))


@pytest.fixture
def mock_operation():
    return mock.Mock(name='operation')


@pytest.fixture
def http_future(mock_future_adapter, mock_operation, mock_incoming_response):
    response_adapter_type = mock.Mock(return_value=mock_incoming_response)
    return HttpFuture(
        future=mock_future_adapter,
        response_adapter=response_adapter_type,
        operation=mock_operation,
    )


@pytest.fixture
def fallback_result():
    return mock.Mock(name='fallback result')


def test_fallback_result(fallback_result, mock_future_adapter, mock_operation, http_future):
    mock_future_adapter.result.side_effect = BravadoTimeoutError()
    mock_operation.swagger_spec.config = {
        'bravado': BravadoConfig.from_config_dict({'disable_fallback_results': False})
    }

    response = http_future.response(fallback_result=lambda e: fallback_result)

    assert response.result == fallback_result
    assert response.metadata.is_fallback_result is True
    assert response.metadata.handled_exception_info[0] is BravadoTimeoutError


def test_no_fallback_result_if_not_in_exceptions_to_catch(fallback_result, mock_future_adapter, http_future):
    mock_future_adapter.result.side_effect = BravadoTimeoutError()

    with pytest.raises(BravadoTimeoutError):
        http_future.response(
            fallback_result=lambda e: fallback_result,
            exceptions_to_catch=(HTTPInternalServerError,),
        )


def test_no_fallback_result_if_not_provided(mock_future_adapter, http_future):
    mock_future_adapter.result.side_effect = BravadoTimeoutError()

    with pytest.raises(BravadoTimeoutError):
        http_future.response()


def test_no_fallback_result_if_config_disabled(mock_future_adapter, mock_operation, http_future):
    mock_future_adapter.result.side_effect = BravadoTimeoutError()
    mock_operation.swagger_spec.config = {
        'bravado': BravadoConfig.from_config_dict({'disable_fallback_results': True})
    }

    with pytest.raises(BravadoTimeoutError):
        http_future.response(fallback_result=lambda e: None)


def test_force_fallback_result(mock_operation, fallback_result, http_future):
    http_future.request_config = RequestConfig(
        {'force_fallback_result': True},
        also_return_response_default=False,
    )
    mock_operation.swagger_spec.config = {
        'bravado': BravadoConfig.from_config_dict({})
    }

    with mock.patch('bravado.http_future.unmarshal_response', autospec=True):
        response = http_future.response(fallback_result=lambda e: fallback_result)

    assert response.result == fallback_result
    assert response.metadata.is_fallback_result is True
    assert response.metadata.handled_exception_info[0] is ForcedFallbackResultError


def test_no_force_fallback_result_if_disabled(http_future, mock_operation, mock_incoming_response, fallback_result):
    http_future.request_config = RequestConfig(
        {'force_fallback_result': True},
        also_return_response_default=False,
    )
    mock_operation.swagger_spec.config = {
        'bravado': BravadoConfig.from_config_dict({'disable_fallback_results': True})
    }

    with mock.patch('bravado.http_future.unmarshal_response', autospec=True):
        response = http_future.response(fallback_result=lambda e: fallback_result)

    assert response.result == mock_incoming_response.swagger_result


def test_custom_response_metadata(mock_operation, http_future):
    mock_operation.swagger_spec.config = {
        'bravado': BravadoConfig.from_config_dict(
            {'response_metadata_class': 'tests.http_future.HttpFuture.response_test.ResponseMetadata'})
    }

    with mock.patch('bravado.http_future.unmarshal_response'):
        response = http_future.response()
    assert response.metadata.__class__ is ResponseMetadata
