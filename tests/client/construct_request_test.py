# -*- coding: utf-8 -*-
import pytest
from bravado_core.operation import Operation
from mock import patch

from bravado.client import CallableOperation
from bravado.client import construct_request


@pytest.mark.parametrize('timeout_kv', [
    ('timeout', 1),
    ('connect_timeout', 2),
])
@patch('bravado.client.marshal_param')
def test_with_timeouts(
    mock_marshal_param, minimal_swagger_spec,
    getPetById_spec, request_dict, timeout_kv,
):
    request_dict['url'] = '/pet/{petId}'
    op = CallableOperation(Operation.from_spec(
        minimal_swagger_spec, '/pet/{petId}', 'get', getPetById_spec))
    k, v = timeout_kv
    request = construct_request(op, request_options={k: v}, petId=34, api_key='foo')
    assert request[k] == v
    assert mock_marshal_param.call_count == 2


@pytest.mark.parametrize('header_name, header_value', [
    ('boolean', True),
    ('integer', 1),
    ('float', 2.0),
])
@patch('bravado.client.marshal_param')
def test_with_not_string_headers(
    mock_marshal_param, minimal_swagger_spec,
    getPetById_spec, request_dict, header_name, header_value,
):
    request_dict['url'] = '/pet/{petId}'
    op = CallableOperation(Operation.from_spec(
        minimal_swagger_spec, '/pet/{petId}', 'get', getPetById_spec))
    request = construct_request(op, request_options={'headers': {header_name: header_value}}, petId=34, api_key='foo')
    assert request['headers'][header_name] == str(header_value)
    assert mock_marshal_param.call_count == 2
