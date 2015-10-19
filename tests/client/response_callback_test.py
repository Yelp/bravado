import pytest
from mock import Mock, patch
from bravado_core.exception import MatchingResponseNotFound
from bravado_core.operation import Operation
from bravado_core.response import IncomingResponse

from bravado.client import response_callback
from bravado.exception import HTTPError


def test_5XX():
    incoming_response = Mock(spec=IncomingResponse, status_code=500)
    operation = Mock(spec=Operation)
    with pytest.raises(HTTPError) as excinfo:
        response_callback(incoming_response, operation)
    assert excinfo.value.response.status_code == 500


@patch('bravado.client.unmarshal_response', return_value=99)
def test_2XX(_1):
    incoming_response = Mock(spec=IncomingResponse)
    incoming_response.status_code = 200
    operation = Mock(spec=Operation)
    response_callback(incoming_response, operation)
    assert incoming_response.swagger_result == 99


@patch('bravado.client.unmarshal_response',
       side_effect=MatchingResponseNotFound('boo'))
def test_2XX_matching_response_not_found_in_spec(_1):
    incoming_response = Mock(spec=IncomingResponse, status_code=200)
    operation = Mock(spec=Operation)
    with pytest.raises(HTTPError) as excinfo:
        response_callback(incoming_response, operation)
    assert excinfo.value.response.status_code == 200
    assert excinfo.value.message == 'boo'


@patch('bravado.client.unmarshal_response',
       side_effect=MatchingResponseNotFound)
def test_4XX_matching_response_not_found_in_spec(_1):
    incoming_response = Mock(spec=IncomingResponse, status_code=404)
    operation = Mock(spec=Operation)
    with pytest.raises(HTTPError) as excinfo:
        response_callback(incoming_response, operation)
    assert excinfo.value.response.status_code == 404


@patch('bravado.client.unmarshal_response', return_value={'msg': 'Not found'})
def test_4XX(_1):
    incoming_response = Mock(spec=IncomingResponse, status_code=404)
    operation = Mock(spec=Operation)
    with pytest.raises(HTTPError) as excinfo:
        response_callback(incoming_response, operation)
    assert excinfo.value.response.status_code == 404
    assert excinfo.value.swagger_result == {'msg': 'Not found'}
