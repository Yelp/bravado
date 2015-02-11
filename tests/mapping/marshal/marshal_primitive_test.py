import pytest

from bravado.mapping.marshal import marshal_primitive
from bravado.mapping.param import Param


@pytest.fixture
def param_spec():
    return {
        'name': 'petId',
        'description': 'ID of pet that needs to be fetched',
        'type': 'integer',
        'format': 'int64',
    }


def test_path(empty_swagger_spec, param_spec):
    param_spec['in'] = 'path'
    param = Param(empty_swagger_spec, param_spec)
    request = {'url': '/pet/{petId}'}
    marshal_primitive(param, 34, request)
    assert '/pet/34' == request['url']


def test_query(empty_swagger_spec, param_spec):
    param_spec['in'] = 'query'
    param = Param(empty_swagger_spec, param_spec)
    request = {
        'params': {}
    }
    marshal_primitive(param, 34, request)
    assert {'petId': 34} == request['params']


def test_header(empty_swagger_spec, param_spec):
    param_spec['in'] = 'header'
    param = Param(empty_swagger_spec, param_spec)
    request = {
        'headers': {}
    }
    marshal_primitive(param, 34, request)
    assert {'petId': 34} == request['headers']


@pytest.mark.xfail(reason='TODO')
def test_formData():
    assert False


@pytest.mark.xfail(reason='TODO')
def test_body():
    assert False
