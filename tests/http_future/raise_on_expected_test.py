# -*- coding: utf-8 -*-
import pytest
from bravado_core.response import IncomingResponse
try:
    from unittest.mock import Mock
except ImportError:
    from mock import Mock

from bravado.exception import HTTPError
from bravado.http_future import raise_on_expected


def test_2XX():
    http_response = Mock(
        spec=IncomingResponse,
        status_code=200,
        swagger_result='hello world')

    # no exception raised == success
    raise_on_expected(http_response)


def test_non_2XX():
    http_response = Mock(
        spec=IncomingResponse,
        status_code=404,
        swagger_result={'error': 'Object not found'})

    with pytest.raises(HTTPError) as excinfo:
        raise_on_expected(http_response)
    assert 'Object not found' in str(excinfo.value)
