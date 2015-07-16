from mock import patch
import pytest

from bravado_core.operation import Operation
from bravado_core.spec import Spec

from bravado.client import OperationDecorator


@pytest.fixture
def getPetById_spec(petstore_dict):
    op = petstore_dict['paths']['/pet/{petId}']['get'].copy()
    op.update({'deprecated': True,
               'x-deprecated-date': 'foo',
               'x-removal-date': 'bar'})
    return op


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
@patch('bravado.client.log.warn')
def test_with_mocks(mock_log, _, minimal_swagger_spec, getPetById_spec):
    op = OperationDecorator(Operation.from_spec(
        minimal_swagger_spec, '/pet/{petId}', 'get', getPetById_spec))
    op.log_warning_for_deprecated_op()
    mock_log.assert_called_once_with(
        '[DEPRECATED] getPetById has now been deprecated.'
        ' Deprecation date: foo, Removal date: bar')
