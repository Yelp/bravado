from bravado.mapping.spec import Spec
from bravado.mapping.operation import Operation


def test_returns_operation_id_from_operation_spec():
    spec = Spec(spec_dict={})
    operation_dict = {'operationId': 'getPetById'}
    operation = Operation(spec, '/pet/{petId}', 'get', operation_dict)
    assert 'getPetById' == operation.operation_id


def test_returns_generated_operation_id_when_missing_from_operation_spec():
    spec = Spec(spec_dict={})
    operation_dict = {}
    operation = Operation(spec, '/pet', 'get', operation_dict)
    assert 'get_pet' == operation.operation_id


def test_returns_generated_operation_id_with_path_parameters():
    spec = Spec(spec_dict={})
    operation_dict = {}
    operation = Operation(spec, '/pet/{petId}', 'get', operation_dict)
    assert 'get_pet_petId' == operation.operation_id


