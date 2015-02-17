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


def test_string_in_query(empty_swagger_spec, string_param_spec, request_dict):
    param = Param(empty_swagger_spec, string_param_spec)
    expected = request_dict.copy()
    expected['params']['username'] = 'darwin'
    marshal_param(param, 'darwin', request_dict)
    assert expected == request_dict


def test_array_in_query(empty_swagger_spec, array_param_spec, request_dict):
    param = Param(empty_swagger_spec, array_param_spec)
    value = ['cat', 'dog', 'bird']
    expected = request_dict.copy()
    expected['params']['animals'] = value
    marshal_param(param, value, request_dict)
    assert expected == request_dict


# @pytest.fixture
# def param_spec():
#     return {
#         'name': 'petId',
#         'description': 'ID of pet that needs to be fetched',
#         'type': 'integer',
#         'format': 'int64',
#     }

# def test_path(empty_swagger_spec, param_spec):
#     param_spec['in'] = 'path'
#     param = Param(empty_swagger_spec, param_spec)
#     request = {'url': '/pet/{petId}'}
#     marshal_primitive(param, 34, request)
#     assert '/pet/34' == request['url']
#
#
# def test_query(empty_swagger_spec, param_spec):
#     param_spec['in'] = 'query'
#     param = Param(empty_swagger_spec, param_spec)
#     request = {
#         'params': {}
#     }
#     marshal_primitive(param, 34, request)
#     assert {'petId': 34} == request['params']
#
#
# def test_header(empty_swagger_spec, param_spec):
#     param_spec['in'] = 'header'
#     param = Param(empty_swagger_spec, param_spec)
#     request = {
#         'headers': {}
#     }
#     marshal_primitive(param, 34, request)
#     assert {'petId': 34} == request['headers']
#
#
# @pytest.mark.xfail(reason='TODO')
# def test_formData():
#     assert False
#
#
# @pytest.mark.xfail(reason='TODO')
# def test_body():
#     assert False
