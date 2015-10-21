from bravado_core.operation import Operation
from mock import patch
import pytest

from bravado.client import CallableOperation, construct_request


@pytest.mark.parametrize('timeout_kv', [
    ('timeout', 1),
    ('connect_timeout', 2),
])
@patch('bravado.client.marshal_param')
def test_with_timeouts(mock_marshal_param, minimal_swagger_spec,
                       getPetById_spec, request_dict, timeout_kv):
    request_dict['url'] = '/pet/{petId}'
    op = CallableOperation(Operation.from_spec(
        minimal_swagger_spec, '/pet/{petId}', 'get', getPetById_spec))
    k, v = timeout_kv
    request = construct_request(op, request_options={k: v}, petId=34)
    assert request[k] == v
    assert mock_marshal_param.call_count == 1
