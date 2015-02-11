import pytest

from bravado.mapping.marshal import marshal_array
from bravado.mapping.param import Param


@pytest.fixture
def param_spec():
    return {
        'name': 'status',
        'in': 'TEST WILL REPLACE THIS',
        'description': 'Status values that need to be considered for filter',
        'required': False,
        'type': 'array',
        'items': {
            'type': 'string'
        },
        'collectionFormat': 'multi',
        'default': 'available'
    }


def test_query(empty_swagger_spec, param_spec):
    param_spec['in'] = 'query'
    param = Param(empty_swagger_spec, param_spec)
    request = {
        'params': {}
    }
    marshal_array(param, ['a', 'b', 'c'], request)
    assert {'status': ['a', 'b', 'c']} == request['params']


def test_header(empty_swagger_spec, param_spec):
    param_spec['in'] = 'header'
    param = Param(empty_swagger_spec, param_spec)
    request = {
        'headers': {}
    }
    marshal_array(param, ['a', 'b', 'c'], request)
    assert {'status': ['a', 'b', 'c']} == request['headers']


@pytest.mark.xfail(reason='TODO')
def test_formData():
    assert False


@pytest.mark.xfail(reason='TODO')
def test_body():
    assert False
