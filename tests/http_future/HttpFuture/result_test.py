from concurrent.futures import Future

from bravado_core.response import IncomingResponse
from mock import Mock, patch
import pytest

from bravado.http_future import HTTPError, HttpFuture


def test_no_response_callback():
    # This use case is for http requests that are made outside of the
    # swagger spec e.g. retrieving the swagger schema
    response_adapter_instance = Mock(spec=IncomingResponse)
    response_adapter_type = Mock(return_value=response_adapter_instance)
    http_future = HttpFuture(
        future=Mock(spec=Future),
        response_adapter=response_adapter_type,
        callback=None)

    assert response_adapter_instance == http_future.result()


def test_200_success():
    response_callback = Mock(return_value='hello world')
    response_adapter_instance = Mock(spec=IncomingResponse, status_code=200)
    response_adapter_type = Mock(return_value=response_adapter_instance)

    http_future = HttpFuture(
        future=Mock(spec=Future),
        response_adapter=response_adapter_type,
        callback=response_callback)

    assert 'hello world' == http_future.result()


@patch('bravado.http_future.raise_http_error_based_on_status',
       side_effect=HTTPError)
def test_4XX_5XX_failure(_):
    response_callback = Mock(return_value='hello world')
    response_adapter_instance = Mock(spec=IncomingResponse, status_code=400)
    response_adapter_type = Mock(return_value=response_adapter_instance)

    http_future = HttpFuture(
        future=Mock(spec=Future),
        response_adapter=response_adapter_type,
        callback=response_callback)

    with pytest.raises(HTTPError):
        http_future.result()
