from mock import Mock
import pytest

from bravado.mapping.operation import Operation
from bravado.mapping.param import Param, unmarshal_param
from bravado.mapping.request import RequestLike


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
        },
        'collectionFormat': 'multi',
    }


@pytest.fixture
def param_spec():
    return {
        'name': 'petId',
        'description': 'ID of pet that needs to be fetched',
        'type': 'integer',
        'format': 'int64',
    }


def test_path_string(empty_swagger_spec, param_spec):
    param_spec['in'] = 'path'
    param = Param(empty_swagger_spec, Mock(spec=Operation), param_spec)
    request = Mock(spec=RequestLike, path={'petId': '34'})
    assert 34 == unmarshal_param(param, request)


def test_query_string(empty_swagger_spec, string_param_spec):
    param = Param(empty_swagger_spec, Mock(spec=Operation), string_param_spec)
    request = Mock(spec=RequestLike, query={'username': 'darwin'})
    assert 'darwin' == unmarshal_param(param, request)


def test_query_array(empty_swagger_spec, array_param_spec):
    param = Param(empty_swagger_spec, Mock(spec=Operation), array_param_spec)
    request = Mock(
        spec=RequestLike,
        query={'animals': ['cat', 'dog', 'mouse']})
    assert ['cat', 'dog', 'mouse'] == unmarshal_param(param, request)


def test_header_string(empty_swagger_spec, param_spec):
    param_spec['in'] = 'header'
    param_spec['type'] = 'string'
    param_spec['name'] = 'X-Source-ID'
    del param_spec['format']
    param = Param(empty_swagger_spec, Mock(spec=Operation), param_spec)
    request = Mock(spec=RequestLike, headers={'X-Source-ID': 'foo'})
    assert 'foo' == unmarshal_param(param, request)


def test_formData_integer(empty_swagger_spec, param_spec):
    param_spec['in'] = 'formData'
    param = Param(empty_swagger_spec, Mock(spec=Operation), param_spec)
    request = Mock(spec=RequestLike, form={'petId': '34'})
    assert 34 == unmarshal_param(param, request)


def test_formData_file(empty_swagger_spec, param_spec):
    param_spec['in'] = 'formData'
    param_spec['type'] = 'file'
    param_spec['name'] = 'selfie'
    param = Param(
        empty_swagger_spec,
        Mock(spec=Operation, consumes=['multipart/form-data']),
        param_spec)
    request = Mock(spec=RequestLike, files={'selfie': '<imagine binary data>'})
    assert '<imagine binary data>' == unmarshal_param(param, request)


def test_body(empty_swagger_spec, param_spec):
    param_spec['in'] = 'body'
    param_spec['schema'] = {
        'type': 'integer'
    }
    del param_spec['type']
    del param_spec['format']
    param = Param(empty_swagger_spec, Mock(spec=Operation), param_spec)
    request = Mock(spec=RequestLike, json=Mock(return_value=34))
    value = unmarshal_param(param, request)
    assert 34 == value
