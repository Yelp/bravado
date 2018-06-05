# -*- coding: utf-8 -*-
import mock
import pytest
from bravado_core.response import IncomingResponse

from bravado.client import SwaggerClient
from bravado.exception import BravadoTimeoutError
from bravado.http_future import HttpFuture
from bravado.response import BravadoResponseMetadata
from tests.conftest import processed_default_config


class ResponseMetadata(BravadoResponseMetadata):
    pass


@pytest.fixture
def getPetById_spec(petstore_dict):
    return petstore_dict['paths']['/pet/{petId}']['get']


@pytest.fixture
def petstore_client(petstore_dict):
    client = SwaggerClient.from_spec(petstore_dict, origin_url='http://localhost/')
    return client


@pytest.fixture
def http_future(mock_future_adapter, petstore_client):
    response_adapter_instance = mock.Mock(spec=IncomingResponse, status_code=200, swagger_result=None)
    response_adapter_type = mock.Mock(return_value=response_adapter_instance)
    return HttpFuture(
        future=mock_future_adapter,
        response_adapter=response_adapter_type,
        operation=petstore_client.pet.getPetById,
    )


def test_fallback_result(mock_future_adapter, http_future, petstore_client):
    fallback_result = {'name': '', 'photoUrls': []}
    mock_future_adapter.result.side_effect = BravadoTimeoutError()

    response = http_future.response(fallback_result=lambda e: fallback_result)

    assert response.result == petstore_client.get_model('Pet').unmarshal(fallback_result)
    assert response.metadata.is_fallback_result is True
    assert response.metadata.handled_exception_info[0] is BravadoTimeoutError


def test_no_fallback_result_if_not_provided(mock_future_adapter, http_future):
    mock_future_adapter.result.side_effect = BravadoTimeoutError()

    with pytest.raises(BravadoTimeoutError):
        http_future.response()


def test_no_fallback_result_if_config_disabled(mock_future_adapter, http_future, petstore_client):
    mock_future_adapter.result.side_effect = BravadoTimeoutError()
    petstore_client.swagger_spec.config['bravado'] = processed_default_config(disable_fallback_results=True)

    with pytest.raises(BravadoTimeoutError):
        http_future.response(fallback_result=lambda e: None)


def test_custom_response_metadata(http_future, petstore_client):
    petstore_client.swagger_spec.config['bravado'] = processed_default_config(
        response_metadata_class=ResponseMetadata,
    )

    with mock.patch('bravado.http_future.unmarshal_response'):
        response = http_future.response()
    assert response.metadata.__class__ is ResponseMetadata
