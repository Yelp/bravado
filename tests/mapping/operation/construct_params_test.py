from mock import patch
import pytest

from bravado.mapping.operation import Operation


@pytest.fixture
def getPetById_spec(petstore_dict):
    """
    :return: operation spec in dict form
    """
    return petstore_dict['paths']['/pet/{petId}']['get']


def test_simple(empty_swagger_spec, getPetById_spec, request_dict):

    @patch('bravado.mapping.operation.marshal_param')
    def test_with_mocks(mock_marshal_param):
        request_dict['url'] = '/pet/{petId}'
        op = Operation.from_spec(
            empty_swagger_spec, '/pet/{petId}', 'get', getPetById_spec)
        op.construct_params(request_dict, {'petId': 34})
        assert 1 == mock_marshal_param.call_count

    test_with_mocks()


def test_no_params(empty_swagger_spec, request_dict):

    @patch('bravado.mapping.operation.marshal_param')
    def test_with_mocks(mock_marshall_param):
        op = Operation.from_spec(empty_swagger_spec, '/pet', 'get', {})
        op.construct_params(request_dict, params_dict={})
        assert 0 == mock_marshall_param.call_count

    test_with_mocks()


def test_extra_parameter_error(empty_swagger_spec, request_dict):
    op = Operation.from_spec(empty_swagger_spec, '/pet', 'get', {})
    with pytest.raises(TypeError) as excinfo:
        op.construct_params(request_dict, params_dict={'extra_param': 'bar'})
    assert 'does not have parameter' in str(excinfo.value)


def test_required_parameter_missing(empty_swagger_spec, getPetById_spec, request_dict):
    request_dict['url'] = '/pet/{petId}'
    op = Operation.from_spec(empty_swagger_spec, '/pet/{petId}', 'get', getPetById_spec)
    with pytest.raises(TypeError) as excinfo:
        op.construct_params(request_dict, params_dict={})
    assert 'required parameter' in str(excinfo.value)


def test_non_required_parameter_with_default_used(
        empty_swagger_spec, getPetById_spec, request_dict):

    @patch('bravado.mapping.operation.marshal_param')
    def test_with_mocks(mock_marshal_param):
        del getPetById_spec['parameters'][0]['required']
        getPetById_spec['parameters'][0]['default'] = 99
        request_dict['url'] = '/pet/{petId}'
        op = Operation.from_spec(empty_swagger_spec, '/pet/{petId}', 'get', getPetById_spec)
        op.construct_params(request_dict, params_dict={})
        assert 1 == mock_marshal_param.call_count

    test_with_mocks()
