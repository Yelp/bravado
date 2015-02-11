import pytest

from bravado.mapping.param import Param, marshal_param


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


def test_string_in_query(swagger_object, string_param_spec, request_dict):
    param = Param(swagger_object, string_param_spec)
    expected = request_dict.copy()
    expected['params']['username'] = 'darwin'
    marshal_param(param, 'darwin', request_dict)
    assert expected == request_dict


def test_array_in_query(swagger_object, array_param_spec, request_dict):
    param = Param(swagger_object, array_param_spec)
    value = ['cat', 'dog', 'bird']
    expected = request_dict.copy()
    expected['params']['animals'] = value
    marshal_param(param, value, request_dict)
    assert expected == request_dict

