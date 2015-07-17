from mock import patch
import pytest

from bravado_core.operation import Operation
from bravado_core.spec import Spec

from bravado.client import OperationDecorator


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


@patch('bravado.client.marshal_param')
@patch('bravado.client.warnings.warn')
def test_warn(mock_warn, _, minimal_swagger_spec, getPetById_spec):
    op_spec = getPetById_spec.copy()
    op_spec.update({'deprecated': True,
                    'x-deprecated-date': 'foo',
                    'x-removal-date': 'bar'})
    op = OperationDecorator(Operation.from_spec(
        minimal_swagger_spec, '/pet/{petId}', 'get', op_spec))
    op.log_warning_for_deprecated_op()
    mock_warn.assert_called_once_with(
        '[DEPRECATED] getPetById has now been deprecated.'
        ' Deprecation date: foo, Removal date: bar', Warning)


@patch('bravado.client.marshal_param')
@patch('bravado.client.warnings.warn')
def test_no_warn_if_false(mock_warn, _, minimal_swagger_spec, getPetById_spec):
    op_spec = getPetById_spec.copy()
    op_spec.update({'deprecated': False})
    op = OperationDecorator(Operation.from_spec(
        minimal_swagger_spec, '/pet/{petId}', 'get', op_spec))
    op.log_warning_for_deprecated_op()
    assert not mock_warn.called


@patch('bravado.client.marshal_param')
@patch('bravado.client.warnings.warn')
def test_no_warn_if_deprecate_flag_not_present(
        mock_warn, _, minimal_swagger_spec, getPetById_spec):
    op = OperationDecorator(Operation.from_spec(
        minimal_swagger_spec, '/pet/{petId}', 'get', getPetById_spec))
    op.log_warning_for_deprecated_op()
    assert not mock_warn.called
