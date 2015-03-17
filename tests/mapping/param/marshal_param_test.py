from mock import Mock
import pytest

from bravado.http_client import APP_JSON
from bravado.mapping.param import Param, marshal_param
from bravado.mapping.operation import Operation


@pytest.fixture
def request_dict():
    return {
        'params': {}
    }


@pytest.fixture
def string_param_spec():
    return {
        'name': 'username',
        'in': 'query',
        'description': 'Short name of the user',
        'type': 'string',
    }


@pytest.fixture
def array_param_spec():
    return {
        'name': 'animals',
        'in': 'query',
        'description': 'List of animals',
        'type': 'array',
        'items': {
            'type': 'string'
        }
    }


@pytest.fixture
def param_spec():
    return {
        'name': 'petId',
        'description': 'ID of pet that needs to be fetched',
        'type': 'integer',
        'format': 'int64',
    }


def test_query_string(empty_swagger_spec, string_param_spec, request_dict):
    param = Param(empty_swagger_spec, Mock(spec=Operation), string_param_spec)
    expected = request_dict.copy()
    expected['params']['username'] = 'darwin'
    marshal_param(param, 'darwin', request_dict)
    assert expected == request_dict


def test_query_array(empty_swagger_spec, array_param_spec, request_dict):
    param = Param(empty_swagger_spec, Mock(spec=Operation), array_param_spec)
    value = ['cat', 'dog', 'bird']
    expected = request_dict.copy()
    expected['params']['animals'] = value
    marshal_param(param, value, request_dict)
    assert expected == request_dict


def test_path_string(empty_swagger_spec, param_spec):
    param_spec['in'] = 'path'
    param = Param(empty_swagger_spec, Mock(spec=Operation), param_spec)
    request = {'url': '/pet/{petId}'}
    marshal_param(param, 34, request)
    assert '/pet/34' == request['url']


def test_header_string(empty_swagger_spec, param_spec):
    param_spec['in'] = 'header'
    param_spec['type'] = 'string'
    del param_spec['format']
    param = Param(empty_swagger_spec, Mock(spec=Operation), param_spec)
    request = {
        'headers': {}
    }
    marshal_param(param, '34', request)
    assert {'petId': '34'} == request['headers']


def test_body(empty_swagger_spec, param_spec):
    param_spec['in'] = 'body'
    param_spec['schema'] = {
        'type': 'integer'
    }
    del param_spec['type']
    del param_spec['format']
    param = Param(empty_swagger_spec, Mock(spec=Operation), param_spec)
    request = {
        'headers': {
        }
    }
    marshal_param(param, 34, request)
    assert '34' == request['data']
    assert APP_JSON == request['headers']['Content-Type']


def test_formData_integer(empty_swagger_spec, param_spec):
    param_spec['in'] = 'formData'
    param = Param(empty_swagger_spec, Mock(spec=Operation), param_spec)
    request = {
        'headers': {
        }
    }
    marshal_param(param, 34, request)
    assert 34 == request['data']['petId']


def test_formData_file(empty_swagger_spec, param_spec, request_dict):
    param_spec['in'] = 'formData'
    param_spec['type'] = 'file'
    param = Param(
        empty_swagger_spec,
        Mock(spec=Operation, consumes=['multipart/form-data']),
        param_spec)
    marshal_param(param, "i am the contents of a file", request_dict)
    expected = {
        'params': {},
        'file': [('files', ('petId', "i am the contents of a file"))],
    }
    print request_dict
    assert expected == request_dict
