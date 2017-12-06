# -*- coding: utf-8 -*-
import pytest
from bravado_core.exception import MatchingResponseNotFound
from bravado_core.operation import Operation
from bravado_core.response import IncomingResponse
from mock import Mock
from mock import patch

from bravado.exception import HTTPError
from bravado.http_future import unmarshal_response


@pytest.fixture
def mock_unmarshal_response_inner():
    with patch('bravado.http_future.unmarshal_response_inner') as m:
        yield m


def test_5XX():
    incoming_response = Mock(spec=IncomingResponse, status_code=500)
    operation = Mock(spec=Operation)
    with pytest.raises(HTTPError) as excinfo:
        unmarshal_response(incoming_response, operation)
    assert excinfo.value.response.status_code == 500


def test_2XX(mock_unmarshal_response_inner):
    mock_unmarshal_response_inner.return_value = 99
    incoming_response = Mock(spec=IncomingResponse)
    incoming_response.status_code = 200
    operation = Mock(spec=Operation)
    unmarshal_response(incoming_response, operation)
    assert incoming_response.swagger_result == 99


def test_2XX_matching_response_not_found_in_spec(mock_unmarshal_response_inner):
    mock_unmarshal_response_inner.side_effect = MatchingResponseNotFound('boo')
    incoming_response = Mock(spec=IncomingResponse, status_code=200)
    operation = Mock(spec=Operation)
    with pytest.raises(HTTPError) as excinfo:
        unmarshal_response(incoming_response, operation)
    assert excinfo.value.response.status_code == 200
    assert excinfo.value.message == 'boo'


def test_4XX_matching_response_not_found_in_spec(mock_unmarshal_response_inner):
    mock_unmarshal_response_inner.side_effect = MatchingResponseNotFound
    incoming_response = Mock(spec=IncomingResponse, status_code=404)
    operation = Mock(spec=Operation)
    with pytest.raises(HTTPError) as excinfo:
        unmarshal_response(incoming_response, operation)
    assert excinfo.value.response.status_code == 404


def test_4XX(mock_unmarshal_response_inner):
    mock_unmarshal_response_inner.return_value = {'msg': 'Not found'}
    incoming_response = Mock(spec=IncomingResponse, status_code=404)
    operation = Mock(spec=Operation)
    with pytest.raises(HTTPError) as excinfo:
        unmarshal_response(incoming_response, operation)
    assert excinfo.value.response.status_code == 404
    assert excinfo.value.swagger_result == {'msg': 'Not found'}


def test_response_callbacks_executed_on_happy_path(mock_unmarshal_response_inner):
    mock_unmarshal_response_inner.return_value = 99
    incoming_response = Mock(spec=IncomingResponse)
    incoming_response.status_code = 200
    operation = Mock(spec=Operation)
    callback = Mock()
    unmarshal_response(incoming_response, operation,
                       response_callbacks=[callback])
    assert incoming_response.swagger_result == 99
    assert callback.call_count == 1


def test_response_callbacks_executed_on_failure(mock_unmarshal_response_inner):
    mock_unmarshal_response_inner.return_value = 99
    incoming_response = Mock(spec=IncomingResponse, status_code=404)
    operation = Mock(spec=Operation)
    callback = Mock()
    with pytest.raises(HTTPError) as excinfo:
        unmarshal_response(incoming_response, operation,
                           response_callbacks=[callback])
    assert excinfo.value.response.status_code == 404
    assert callback.call_count == 1
