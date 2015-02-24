from mock import Mock
import pytest
import requests.models

from bravado.mapping.operation import handle_response, Operation


def test_RequestsLib_response(empty_swagger_spec):
    response = Mock(spec=requests.models.Response, status_code=200)
    op_spec = {
        'responses': {
            '200': {
                'description': 'success'
            }
        }

    }
    op = Operation(empty_swagger_spec, '/pets/{petId}', 'get', op_spec)
    status_code, value = handle_response(response, op)
    assert 200 == status_code
    assert value is None


def test_unsupported_response_type(empty_swagger_spec):
    response = {}
    op_spec = {
        'responses': {
            '200': {
                'description': 'success'
            }
        }

    }
    op = Operation(empty_swagger_spec, '/pets/{petId}', 'get', op_spec)
    with pytest.raises(NotImplementedError):
        handle_response(response, op)
