from jsonschema.exceptions import ValidationError
import pytest

from bravado.mapping.validate import validate_array


@pytest.fixture
def int_array_spec():
    return {
        'type': 'array',
        'items': {
            'type': 'integer',
        }
    }


def test_minItems_success(int_array_spec):
    int_array_spec['minItems'] = 2
    validate_array(int_array_spec, [1, 2, 3])


def test_minItems_failure(int_array_spec):
    int_array_spec['minItems'] = 2
    with pytest.raises(ValidationError) as excinfo:
        validate_array(int_array_spec, [1])
    assert 'is too short' in str(excinfo)


def test_maxItems_success(int_array_spec):
    int_array_spec['maxItems'] = 2
    validate_array(int_array_spec, [1])


def test_maxItems_failure(int_array_spec):
    int_array_spec['maxItems'] = 2
    with pytest.raises(ValidationError) as excinfo:
        validate_array(int_array_spec, [1, 2, 3, 4])
    assert 'is too long' in str(excinfo)


def test_unqiueItems_true_success(int_array_spec):
    int_array_spec['uniqueItems'] = True
    validate_array(int_array_spec, [1, 2, 3])


def test_uniqueItems_true_failure(int_array_spec):
    int_array_spec['uniqueItems'] = True
    with pytest.raises(ValidationError) as excinfo:
        validate_array(int_array_spec, [1, 2, 1, 4])
    assert 'has non-unique elements' in str(excinfo)


def test_uniqueItems_false(int_array_spec):
    int_array_spec['uniqueItems'] = False
    validate_array(int_array_spec, [1, 2, 3])
    validate_array(int_array_spec, [1, 2, 1, 4])
