from jsonschema.exceptions import ValidationError
import pytest

from bravado.mapping.validate import validate_primitive


def test_integer_success():
    integer_spec = {
        'type': 'integer'
    }
    validate_primitive(integer_spec, 10)
    validate_primitive(integer_spec, -10)


def test_integer_failure():
    integer_spec = {
        'type': 'integer'
    }
    with pytest.raises(ValidationError) as excinfo:
        validate_primitive(integer_spec, 'i am a string')
    assert "is not of type 'integer'" in str(excinfo.value)


def test_boolean_success():
    boolean_spec = {
        'type': 'boolean'
    }
    validate_primitive(boolean_spec, True)
    validate_primitive(boolean_spec, False)


def test_boolean_falure():
    boolean_spec = {
        'type': 'boolean'
    }
    with pytest.raises(ValidationError) as excinfo:
        validate_primitive(boolean_spec, "foo")
    assert "is not of type 'boolean'" in str(excinfo.value)


def test_number_success():
    number_spec = {
        'type': 'number'
    }
    validate_primitive(number_spec, 3.14)


def test_number_failure():
    number_spec = {
        'type': 'number'
    }
    with pytest.raises(ValidationError) as excinfo:
        validate_primitive(number_spec, "foo")
    assert "is not of type 'number'" in str(excinfo.value)


def test_string_success():
    string_spec = {
        'type': 'string'
    }
    validate_primitive(string_spec, 'foo')
    validate_primitive(string_spec, u'bar')


def test_string_failure():
    string_spec = {
        'type': 'string'
    }
    with pytest.raises(ValidationError) as excinfo:
        validate_primitive(string_spec, 999)
    assert "is not of type 'string'" in str(excinfo.value)


def test_doesnt_blow_up_when_spec_has_a_require_key():
    string_spec = {
        'type': 'string',
        'require': True,
    }
    validate_primitive(string_spec, 'foo')
