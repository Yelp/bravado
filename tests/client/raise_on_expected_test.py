from bravado_core.response import IncomingResponse
from mock import Mock
import pytest

from bravado.client import raise_on_expected
from bravado.exception import HTTPError


def test_2XX():
    http_response = Mock(spec=IncomingResponse, status_code=200)
    swagger_return_value = {'msg': 'Request successful'}
    # no error raised == success
    raise_on_expected(http_response, swagger_return_value)


def test_non_2XX():
    http_response = Mock(spec=IncomingResponse, status_code=404)
    with pytest.raises(HTTPError) as excinfo:
        raise_on_expected(
            http_response,
            swagger_return_value={'error': 'Object not found'})
    assert 'Object not found' in str(excinfo.value)
