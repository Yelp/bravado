import pytest

from bravado.mapping.marshal import marshal_primitive
from bravado.mapping.marshal import Param


@pytest.fixture
def param_spec():
    return {
        'name': 'petId',
        'description': 'ID of pet that needs to be fetched',
        'type': 'integer',
        'format': 'int64',
    }


def test_path(swagger_object, param_spec):
    param_spec['in'] = 'path'
    param = Param(swagger_object, param_spec)
    request = {'url': '/pet/{petId}'}
    marshal_primitive(param, 34, request)
    assert '/pet/34' == request['url']


def test_query(swagger_object, param_spec):
    param_spec['in'] = 'query'
    param = Param(swagger_object, param_spec)
    request = {
        'params': {}
    }
    marshal_primitive(param, 34, request)
    assert {'petId': 34} == request['params']


def test_header(swagger_object, param_spec):
    param_spec['in'] = 'header'
    param = Param(swagger_object, param_spec)
    request = {
        'headers': {}
    }
    marshal_primitive(param, 34, request)
    assert {'petId': 34} == request['headers']


def test_formData(swagger_object, param_spec):
    pass


def test_body(swagger_object, param_spec):
    pass
