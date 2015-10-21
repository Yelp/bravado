from bravado_core.operation import Operation
from bravado_core.response import IncomingResponse
from concurrent.futures import Future
from mock import patch, Mock
import pytest

from bravado.http_future import HTTPError, HttpFuture


def test_200_get_swagger_spec():
    response_adapter_instance = Mock(spec=IncomingResponse, status_code=200)
    response_adapter_type = Mock(return_value=response_adapter_instance)
    http_future = HttpFuture(
        concurrent_future=Mock(spec=Future),
        response_adapter=response_adapter_type)

    assert response_adapter_instance == http_future.result()


def test_500_get_swagger_spec():
    response_adapter_instance = Mock(spec=IncomingResponse, status_code=500)
    response_adapter_type = Mock(return_value=response_adapter_instance)

    with pytest.raises(HTTPError) as excinfo:
        HttpFuture(
            concurrent_future=Mock(spec=Future),
            response_adapter=response_adapter_type).result()

    assert excinfo.value.response.status_code == 500


@patch('bravado.http_future.unmarshal_response')
def test_200_service_call(_):
    response_adapter_instance = Mock(
        spec=IncomingResponse,
        status_code=200,
        swagger_result='hello world')

    response_adapter_type = Mock(return_value=response_adapter_instance)

    http_future = HttpFuture(
        concurrent_future=Mock(spec=Future),
        response_adapter=response_adapter_type,
        operation=Mock(spec=Operation))

    assert 'hello world' == http_future.result()


@patch('bravado.http_future.unmarshal_response')
def test_400_service_call(mock_unmarshal_response):
    response_adapter_instance = Mock(
        spec=IncomingResponse,
        status_code=400,
        swagger_result={'error': 'Blah'})
    mock_unmarshal_response.side_effect = HTTPError(response_adapter_instance)
    response_adapter_type = Mock(return_value=response_adapter_instance)

    http_future = HttpFuture(
        concurrent_future=Mock(spec=Future),
        response_adapter=response_adapter_type,
        operation=Mock(spec=Operation))

    with pytest.raises(HTTPError) as excinfo:
        http_future.result()
    assert excinfo.value.response.status_code == 400


@patch('bravado.http_future.unmarshal_response')
def test_also_return_response_true(_):
    # Verify HTTPFuture(..., also_return_response=True).result()
    # returns the (swagger_result, http_response) and not just swagger_result
    response_adapter_instance = Mock(
        spec=IncomingResponse,
        status_code=200,
        swagger_result='hello world')
    response_adapter_type = Mock(return_value=response_adapter_instance)

    http_future = HttpFuture(
        concurrent_future=Mock(spec=Future),
        response_adapter=response_adapter_type,
        operation=Mock(spec=Operation),
        also_return_response=True)

    swagger_result, http_response = http_future.result()

    assert http_response == response_adapter_instance
    assert swagger_result == 'hello world'
