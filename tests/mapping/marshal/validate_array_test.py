from jsonschema.exceptions import ValidationError
import pytest

from bravado.mapping.marshal import validate_array
from bravado.mapping.marshal import Param
from bravado.exception import SwaggerError


@pytest.fixture
def param_spec():
    return {
        'name': 'status',
        'in': 'query',
        'description': 'Status values that need to be considered for filter',
        'required': False,
        'type': 'array',
        'items': {
            'type': 'string'
        },
        'collectionFormat': 'multi',
        'default': 'available'
    }


def test_valid(swagger_object, param_spec):
    param = Param(swagger_object, param_spec)
    value = validate_array(param, ['a','b','c'])
    assert ['a','b','c'] == value


def test_uses_default(swagger_object, param_spec):
    param_spec['default'] = ['available']
    param = Param(swagger_object, param_spec)
    value = validate_array(param, None)
    assert ['available'] == value


def test_wraps_default_in_array_when_not_array(swagger_object, param_spec):
    param = Param(swagger_object, param_spec)
    value = validate_array(param, None)
    assert ['available'] == value


def test_error_when_required_and_value_is_None(swagger_object, param_spec):
    del param_spec['default']
    param_spec['required'] = True
    param = Param(swagger_object, param_spec)
    with pytest.raises(SwaggerError) as excinfo:
        validate_array(param, None)
    assert 'status cannot be null' in str(excinfo.value)

# ========================================================================
# These validations are not the responsiblity of 'validate_array' but I'm
# testing them anyway to make sure the underlying jsonschema validation
# works as expected and raises the appropriate exception.
# ========================================================================

def test_fails_type_validation(swagger_object, param_spec):
    param = Param(swagger_object, param_spec)
    with pytest.raises(ValidationError) as excinfo:
        validate_array(param, [1, 2, 3])
    assert "Failed validating 'type'" in str(excinfo.value)


def test_fails_minItems_validation(swagger_object, param_spec):
    param_spec['minItems'] = 2
    param = Param(swagger_object, param_spec)
    with pytest.raises(ValidationError) as excinfo:
        validate_array(param, ['a'])
    assert "is too short" in str(excinfo.value)


def test_fails_maxItems_validation(swagger_object, param_spec):
    param_spec['maxItems'] = 2
    param = Param(swagger_object, param_spec)
    with pytest.raises(ValidationError) as excinfo:
        validate_array(param, ['a', 'b', 'c'])
    assert "is too long" in str(excinfo.value)


def test_fails_uniqueItems_validation(swagger_object, param_spec):
    param_spec['uniqueItems'] = True
    param = Param(swagger_object, param_spec)
    with pytest.raises(ValidationError) as excinfo:
        validate_array(param, ['a', 'a', 'a'])
    assert "has non-unique elements" in str(excinfo.value)
