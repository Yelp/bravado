from mock import patch
import pytest

from bravado.mapping.operation import Operation
from bravado.mapping.spec import Spec


@pytest.fixture
def getPetById_spec(petstore_dict):
    """
    :return: operation spec in dict form
    """
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

    @patch('bravado.mapping.operation.marshal_param')
    def test_with_mocks(mock_marshal_param):
        request_dict['url'] = '/pet/{petId}'
        op = Operation.from_spec(
            minimal_swagger_spec, '/pet/{petId}', 'get', getPetById_spec)
        op.construct_params(request_dict, op_kwargs={'petId': 34})
        assert 1 == mock_marshal_param.call_count

    test_with_mocks()


def test_no_params(minimal_swagger_spec, request_dict):

    @patch('bravado.mapping.operation.marshal_param')
    def test_with_mocks(mock_marshal_param):
        get_op = minimal_swagger_spec.spec_dict['paths']['/pet/{petId}']['get']
        del get_op['parameters'][0]
        op = Operation.from_spec(
            minimal_swagger_spec, '/pet/{petId}', 'get', {})
        op.construct_params(request_dict, op_kwargs={})
        assert 0 == mock_marshal_param.call_count

    test_with_mocks()


def test_extra_parameter_error(minimal_swagger_spec, request_dict):
    op = Operation.from_spec(minimal_swagger_spec, '/pet/{petId}', 'get', {})
    with pytest.raises(TypeError) as excinfo:
        op.construct_params(request_dict, op_kwargs={'extra_param': 'bar'})
    assert 'does not have parameter' in str(excinfo.value)


def test_required_parameter_missing(
        minimal_swagger_spec, getPetById_spec, request_dict):
    request_dict['url'] = '/pet/{petId}'
    op = Operation.from_spec(
        minimal_swagger_spec, '/pet/{petId}', 'get', getPetById_spec)
    with pytest.raises(TypeError) as excinfo:
        op.construct_params(request_dict, op_kwargs={})
    assert 'required parameter' in str(excinfo.value)


def test_non_required_parameter_with_default_used(
        minimal_swagger_spec, getPetById_spec, request_dict):

    @patch('bravado.mapping.operation.marshal_param')
    def test_with_mocks(mock_marshal_param):
        del getPetById_spec['parameters'][0]['required']
        getPetById_spec['parameters'][0]['default'] = 99
        request_dict['url'] = '/pet/{petId}'
        op = Operation.from_spec(
            minimal_swagger_spec, '/pet/{petId}', 'get', getPetById_spec)
        op.construct_params(request_dict, op_kwargs={})
        assert 1 == mock_marshal_param.call_count

    test_with_mocks()
