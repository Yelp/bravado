from jsonschema.exceptions import ValidationError
import pytest

from bravado.mapping.unmarshal import unmarshal_primitive


def test_integer():
    integer_spec = {
        'type': 'integer'
    }
    assert 10 == unmarshal_primitive(integer_spec, 10)
    assert -10 == unmarshal_primitive(integer_spec, -10)


def test_wrong_type():
    integer_spec = {
        'type': 'integer'
    }
    with pytest.raises(ValidationError) as excinfo:
        unmarshal_primitive(integer_spec, 'i am a string')
    assert "is not of type 'integer'" in str(excinfo.value)


def test_boolean():
    boolean_spec = {
        'type': 'boolean'
    }
    assert unmarshal_primitive(boolean_spec, True)
    assert not unmarshal_primitive(boolean_spec, False)


def test_number():
    number_spec = {
        'type': 'number'
    }
    assert 3.14 == unmarshal_primitive(number_spec, 3.14)


def test_string():
    string_spec = {
        'type': 'string'
    }
    assert 'foo' == unmarshal_primitive(string_spec, 'foo')
    assert u'bar' == unmarshal_primitive(string_spec, u'bar')


def test_required_failure():
    integer_spec = {
        'type': 'integer',
        'required': True,
    }
    with pytest.raises(TypeError) as excinfo:
        unmarshal_primitive(integer_spec, None)
    assert 'is a required value' in str(excinfo.value)
