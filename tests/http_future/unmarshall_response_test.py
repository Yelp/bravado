import pytest
from mock import Mock, patch
from bravado_core.exception import MatchingResponseNotFound
from bravado_core.operation import Operation
from bravado_core.response import IncomingResponse

from bravado.exception import HTTPError
from bravado.http_future import unmarshal_response


def test_5XX():
    incoming_response = Mock(spec=IncomingResponse, status_code=500)
    operation = Mock(spec=Operation)
    with pytest.raises(HTTPError) as excinfo:
        unmarshal_response(incoming_response, operation)
    assert excinfo.value.response.status_code == 500


@patch('bravado_core.response.unmarshal_response', return_value=99)
def test_2XX(_1):
    incoming_response = Mock(spec=IncomingResponse)
    incoming_response.status_code = 200
    operation = Mock(spec=Operation)
    unmarshal_response(incoming_response, operation)
    assert incoming_response.swagger_result == 99


@patch('bravado_core.response.unmarshal_response',
       side_effect=MatchingResponseNotFound('boo'))
def test_2XX_matching_response_not_found_in_spec(_1):
    incoming_response = Mock(spec=IncomingResponse, status_code=200)
    operation = Mock(spec=Operation)
    with pytest.raises(HTTPError) as excinfo:
        unmarshal_response(incoming_response, operation)
    assert excinfo.value.response.status_code == 200
    assert excinfo.value.message == 'boo'


@patch('bravado_core.response.unmarshal_response',
       side_effect=MatchingResponseNotFound)
def test_4XX_matching_response_not_found_in_spec(_1):
    incoming_response = Mock(spec=IncomingResponse, status_code=404)
    operation = Mock(spec=Operation)
    with pytest.raises(HTTPError) as excinfo:
        unmarshal_response(incoming_response, operation)
    assert excinfo.value.response.status_code == 404


@patch('bravado_core.response.unmarshal_response',
       return_value={'msg': 'Not found'})
def test_4XX(_1):
    incoming_response = Mock(spec=IncomingResponse, status_code=404)
    operation = Mock(spec=Operation)
    with pytest.raises(HTTPError) as excinfo:
        unmarshal_response(incoming_response, operation)
    assert excinfo.value.response.status_code == 404
    assert excinfo.value.swagger_result == {'msg': 'Not found'}


@patch('bravado_core.response.unmarshal_response', return_value=99)
def test_response_callbacks_executed_on_happy_path(_1):
    incoming_response = Mock(spec=IncomingResponse)
    incoming_response.status_code = 200
    operation = Mock(spec=Operation)
    callback = Mock()
    unmarshal_response(incoming_response, operation,
                       response_callbacks=[callback])
    assert incoming_response.swagger_result == 99
    assert callback.call_count == 1


@patch('bravado_core.response.unmarshal_response', return_value=99)
def test_response_callbacks_executed_on_failure(_1):
    incoming_response = Mock(spec=IncomingResponse, status_code=404)
    operation = Mock(spec=Operation)
    callback = Mock()
    with pytest.raises(HTTPError) as excinfo:
        unmarshal_response(incoming_response, operation,
                           response_callbacks=[callback])
    assert excinfo.value.response.status_code == 404
    assert callback.call_count == 1
