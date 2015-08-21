from mock import patch
import pytest

from bravado_core.exception import SwaggerMappingError
from bravado_core.operation import Operation
from bravado_core.spec import Spec

from bravado.client import CallableOperation


@pytest.fixture
def request_dict():
    return {}


@pytest.fixture
def getPetById_spec(petstore_dict):
    return petstore_dict['paths']['/pet/{petId}']['get']


@pytest.fixture
def minimal_swagger_spec(getPetById_spec):
    spec_dict = {
        'paths': {
            '/pet/{petId}': {
                'get': getPetById_spec
            }
        }
    }
    return Spec(spec_dict)


def test_simple(minimal_swagger_spec, getPetById_spec, request_dict):

    @patch('bravado.client.marshal_param')
    def test_with_mocks(mock_marshal_param):
        request_dict['url'] = '/pet/{petId}'
        op = CallableOperation(Operation.from_spec(
            minimal_swagger_spec, '/pet/{petId}', 'get', getPetById_spec))
        op.construct_params(request_dict, op_kwargs={'petId': 34})
        assert 1 == mock_marshal_param.call_count

    test_with_mocks()


def test_no_params(minimal_swagger_spec, request_dict):

    @patch('bravado.client.marshal_param')
    def test_with_mocks(mock_marshal_param):
        get_op = minimal_swagger_spec.spec_dict['paths']['/pet/{petId}']['get']
        del get_op['parameters'][0]
        op = CallableOperation(Operation.from_spec(
            minimal_swagger_spec, '/pet/{petId}', 'get', {}))
        op.construct_params(request_dict, op_kwargs={})
        assert 0 == mock_marshal_param.call_count
        assert 0 == len(request_dict)

    test_with_mocks()


def test_extra_parameter_error(minimal_swagger_spec, request_dict):
    op = CallableOperation(Operation.from_spec(
        minimal_swagger_spec, '/pet/{petId}', 'get', {}))
    with pytest.raises(SwaggerMappingError) as excinfo:
        op.construct_params(request_dict, op_kwargs={'extra_param': 'bar'})
    assert 'does not have parameter' in str(excinfo.value)


def test_required_parameter_missing(
        minimal_swagger_spec, getPetById_spec, request_dict):
    request_dict['url'] = '/pet/{petId}'
    op = CallableOperation(Operation.from_spec(
        minimal_swagger_spec, '/pet/{petId}', 'get', getPetById_spec))
    with pytest.raises(SwaggerMappingError) as excinfo:
        op.construct_params(request_dict, op_kwargs={})
    assert 'required parameter' in str(excinfo.value)


def test_non_required_parameter_with_default_used(
        minimal_swagger_spec, getPetById_spec, request_dict):

    @patch('bravado.client.marshal_param')
    def test_with_mocks(mock_marshal_param):
        del getPetById_spec['parameters'][0]['required']
        getPetById_spec['parameters'][0]['default'] = 99
        request_dict['url'] = '/pet/{petId}'
        op = CallableOperation(Operation.from_spec(
            minimal_swagger_spec, '/pet/{petId}', 'get', getPetById_spec))
        op.construct_params(request_dict, op_kwargs={})
        assert 1 == mock_marshal_param.call_count

    test_with_mocks()
