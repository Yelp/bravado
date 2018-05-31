# -*- coding: utf-8 -*-
import mock
import pytest
from bravado_core.response import IncomingResponse

from bravado.config import BravadoConfig
from bravado.exception import BravadoTimeoutError
from bravado.http_future import HttpFuture
from bravado.response import BravadoResponseMetadata


class ResponseMetadata(BravadoResponseMetadata):
    pass


def test_fallback_result(mock_future_adapter):
    fallback_result = mock.Mock(name='fallback result')
    mock_future_adapter.result.side_effect = BravadoTimeoutError()
    mock_operation = mock.Mock(name='operation')
    mock_operation.swagger_spec.config = {
        'bravado': BravadoConfig.from_config_dict({'disable_fallback_results': False})
    }

    http_future = HttpFuture(
        future=mock_future_adapter,
        response_adapter=mock.Mock(spec=IncomingResponse),
        operation=mock_operation,
    )

    response = http_future.response(fallback_result=lambda e: fallback_result)

    assert response.result == fallback_result
    assert response.response_metadata.is_fallback_result is True
    assert response.response_metadata.exc_info[0] is BravadoTimeoutError


def test_no_fallback_result_if_config_disabled(mock_future_adapter):
    mock_future_adapter.result.side_effect = BravadoTimeoutError()
    mock_operation = mock.Mock(name='operation')
    mock_operation.swagger_spec.config = {
        'bravado': BravadoConfig.from_config_dict({'disable_fallback_results': True})
    }

    http_future = HttpFuture(
        future=mock_future_adapter,
        response_adapter=mock.Mock(spec=IncomingResponse),
        operation=mock_operation,
    )

    with pytest.raises(BravadoTimeoutError):
        http_future.response(fallback_result=lambda e: None)


def test_custom_response_metadata(mock_future_adapter):
    mock_operation = mock.Mock(name='operation')
    mock_operation.swagger_spec.config = {
        'bravado': BravadoConfig.from_config_dict(
            {'response_metadata_class': 'tests.http_future.HttpFuture.response_test.ResponseMetadata'})
    }
    response_adapter_instance = mock.Mock(spec=IncomingResponse, status_code=200, swagger_result=None)
    response_adapter_type = mock.Mock(return_value=response_adapter_instance)
    http_future = HttpFuture(
        future=mock_future_adapter,
        response_adapter=response_adapter_type,
        operation=mock_operation,
    )

    with mock.patch('bravado.http_future.unmarshal_response'):
        response = http_future.response()
    assert response.response_metadata.__class__ is ResponseMetadata
