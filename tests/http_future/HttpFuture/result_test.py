from concurrent.futures import Future

from bravado_core.response import IncomingResponse
from mock import Mock
import pytest

from bravado.http_future import HTTPError, HttpFuture


def test_200_no_response_callback():
    # This use case is for http requests that are made outside of the
    # swagger spec e.g. retrieving the swagger schema
    response_adapter_instance = Mock(spec=IncomingResponse, status_code=200)
    response_adapter_type = Mock(return_value=response_adapter_instance)
    http_future = HttpFuture(
        future=Mock(spec=Future),
        response_adapter=response_adapter_type,
        callback=None)

    assert response_adapter_instance == http_future.result()


def test_non_2XX_no_response_callback():
    response_adapter_instance = Mock(spec=IncomingResponse, status_code=500)
    response_adapter_type = Mock(return_value=response_adapter_instance)

    with pytest.raises(HTTPError) as excinfo:
        HttpFuture(
            future=Mock(spec=Future),
            response_adapter=response_adapter_type,
            callback=None).result()

    assert excinfo.value.response.status_code == 500


def test_200_with_response_callback():
    response_callback = Mock(return_value='hello world')
    response_adapter_instance = Mock(spec=IncomingResponse, status_code=200)
    response_adapter_type = Mock(return_value=response_adapter_instance)

    http_future = HttpFuture(
        future=Mock(spec=Future),
        response_adapter=response_adapter_type,
        callback=response_callback)

    assert 'hello world' == http_future.result()


def test_non_2XX_with_response_callback():
    response_adapter_instance = Mock(spec=IncomingResponse, status_code=400)
    response_callback = Mock(side_effect=HTTPError(response_adapter_instance))
    response_adapter_type = Mock(return_value=response_adapter_instance)

    http_future = HttpFuture(
        future=Mock(spec=Future),
        response_adapter=response_adapter_type,
        callback=response_callback)

    with pytest.raises(HTTPError) as excinfo:
        http_future.result()
    assert excinfo.value.response.status_code == 400
