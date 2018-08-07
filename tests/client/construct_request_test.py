# -*- coding: utf-8 -*-
import pytest
from bravado_core.operation import Operation
from bravado_core.request import IncomingRequest
from bravado_core.request import unmarshal_request
from mock import mock
from mock import patch

from bravado.client import CallableOperation
from bravado.client import construct_request
from tests.client.conftest import minimal_swagger_spec as build_swagger_spec


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


@pytest.mark.parametrize(
    'swagger_type, swagger_format, header_name, header_value', [
        ('boolean', None, 'boolean', True),
        ('integer', None, 'integer', 1),
        ('number', 'float', 'float', 2.0),
    ],
)
def test_with_not_string_headers(
    minimal_swagger_dict, getPetById_spec, request_dict,
    swagger_type, swagger_format, header_name, header_value,
):
    url = '/pet/{petId}'
    parameter = {
        'name': header_name,
        'in': 'header',
        'required': False,
        'type': swagger_type,
    }
    if swagger_format:
        parameter['format'] = swagger_format
    minimal_swagger_dict['paths'][url]['get']['parameters'].append(parameter)

    minimal_swagger_spec = build_swagger_spec(minimal_swagger_dict)
    request_dict['url'] = url

    operation = Operation.from_spec(
        swagger_spec=minimal_swagger_spec,
        path_name='/pet/{petId}',
        http_method='get',
        op_spec=getPetById_spec,
    )

    petId = 34
    api_key = 'foo'
    request = construct_request(
        operation=operation,
        request_options={'headers': {header_name: header_value}},
        petId=petId,
        api_key=api_key,
    )

    # To unmarshall a request bravado-core needs the request to be wrapped
    # by an object with a specific list of attributes
    request_object = type('IncomingRequest', (IncomingRequest,), {
        'path': {'petId': petId},
        'query': {},
        'form': {},
        'headers': request['headers'],
        'files': mock.Mock(),
    })

    expected_header_value = str(header_value)
    # we need to handle a backwards-incompatible change in bravado-core 5.0.5
    if swagger_type == 'boolean':
        assert request['headers'][header_name] in (expected_header_value, expected_header_value.lower())
    else:
        assert request['headers'][header_name] == expected_header_value

    unmarshalled_request = unmarshal_request(request_object, operation)
    assert unmarshalled_request[header_name] == header_value


def test_use_msgpack(
    minimal_swagger_spec,
    getPetById_spec,
):
    op = CallableOperation(
        Operation.from_spec(
            minimal_swagger_spec,
            '/pet/{petId}',
            'get',
            getPetById_spec
        )
    )
    request = construct_request(
        op,
        request_options={
            'use_msgpack': True,
        },
        petId=1,
    )
    assert request['headers']['Accept'] == 'application/msgpack'
