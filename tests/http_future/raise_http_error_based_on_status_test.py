from bravado_core.response import IncomingResponse
from mock import Mock
import pytest

from bravado.http_future import raise_http_error_based_on_status, HTTPError


def test_200():
    http_response = Mock(spec=IncomingResponse, status_code=200)
    # no error raised == success
    raise_http_error_based_on_status(http_response, 'hello world')


def test_http_error_raised_on_4XX_client_error():
    http_response = Mock(spec=IncomingResponse, status_code=404)
    with pytest.raises(HTTPError) as excinfo:
        raise_http_error_based_on_status(
            http_response, {'error': 'Object not found'})
    assert 'Client Error' in str(excinfo.value)


def test_http_error_raised_on_5XX_server_error():
    http_response = Mock(spec=IncomingResponse, status_code=500)
    with pytest.raises(HTTPError) as excinfo:
        raise_http_error_based_on_status(
            http_response, {'error': 'kaboom'})
    assert 'Server Error' in str(excinfo.value)
