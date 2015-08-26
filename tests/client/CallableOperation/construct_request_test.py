from bravado_core.operation import Operation
from mock import patch
import pytest

from bravado.client import CallableOperation


@pytest.mark.parametrize('timeout_kv', [
    ('timeout', 1),
    ('connect_timeout', 2),
])
@patch('bravado.client.marshal_param')
def test_with_timeouts(_1, minimal_swagger_spec, getPetById_spec, request_dict,
                       timeout_kv):
    request_dict['url'] = '/pet/{petId}'
    op = CallableOperation(Operation.from_spec(
        minimal_swagger_spec, '/pet/{petId}', 'get', getPetById_spec))
    key, value = timeout_kv
    request = op.construct_request(petId=34, _request_options={key: value})
    assert request[key] == value
