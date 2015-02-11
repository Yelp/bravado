import jsonschema
import pytest

from bravado.exception import SwaggerError
from bravado.mapping.marshal import validate_primitive
from bravado.mapping.param import Param


@pytest.fixture
def param_spec():
    return {
        'name': 'petId',
        'in': 'path',
        'description': 'ID of pet that needs to be fetched',
        'type': 'integer',
        'format': 'int64',
    }


def test_success(empty_swagger_spec, param_spec):
    param = Param(empty_swagger_spec, param_spec)
    assert 34 == validate_primitive(param, value=34)


def test_uses_default_when_value_None(empty_swagger_spec, param_spec):
    param_spec['default'] = 99
    param = Param(empty_swagger_spec, param_spec)
    assert 99 == validate_primitive(param, value=None)


def test_skips_default_when_value_not_None(empty_swagger_spec, param_spec):
    param_spec['default'] = 99
    param = Param(empty_swagger_spec, param_spec)
    assert 34 == validate_primitive(param, value=34)


def test_fails_jsonschema_validation(empty_swagger_spec, param_spec):
    param = Param(empty_swagger_spec, param_spec)
    with pytest.raises(jsonschema.ValidationError) as excinfo:
        validate_primitive(param, value="I am not an integer")
    assert "is not of type 'integer'" in str(excinfo.value)


def test_fails_required_validation(empty_swagger_spec, param_spec):
    param_spec['required'] = True
    param = Param(empty_swagger_spec, param_spec)
    with pytest.raises(SwaggerError) as excinfo:
        validate_primitive(param, value=None)
    assert "petId cannot be null" in str(excinfo.value)
