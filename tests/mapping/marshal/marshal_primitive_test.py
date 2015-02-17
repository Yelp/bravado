import mock
import pytest

from jsonschema.exceptions import ValidationError
from bravado.mapping.marshal import marshal_primitive


def test_integer():
    integer_spec = {
        'type': 'integer'
    }
    assert 10 == marshal_primitive(integer_spec, 10)
    assert -10 == marshal_primitive(integer_spec, -10)


def test_wrong_type():
    integer_spec = {
        'type': 'integer'
    }
    with pytest.raises(ValidationError) as excinfo:
        marshal_primitive(integer_spec, 'i am a string')
    assert "is not of type 'integer'" in str(excinfo.value)


def test_boolean():
    boolean_spec = {
        'type': 'boolean'
    }
    assert True == marshal_primitive(boolean_spec, True)
    assert False == marshal_primitive(boolean_spec, False)


def test_number():
    number_spec = {
        'type': 'number'
    }
    assert 3.14 == marshal_primitive(number_spec, 3.14)


def test_string():
    string_spec = {
        'type': 'string'
    }
    assert 'foo' == marshal_primitive(string_spec, 'foo')
    assert u'bar' == marshal_primitive(string_spec, u'bar')


@mock.patch('bravado.mapping.marshal.formatter.to_wire')
@mock.patch('jsonschema.validate')
def test_uses_default_and_skips_formatting_and_validation(mock_to_wire, mock_validate):
    integer_spec = {
        'type': 'integer',
        'default': 10,
    }
    assert 10 == marshal_primitive(integer_spec, None)
    assert mock_to_wire.call_count == 0
    assert mock_validate.call_count == 0


@mock.patch('bravado.mapping.marshal.formatter.to_wire', return_value=99)
@mock.patch('jsonschema.validate')
def test_skips_default(mock_to_wire, mock_validate):
    integer_spec = {
        'type': 'integer',
        'default': 10,
    }
    assert 99 == marshal_primitive(integer_spec, 99)
    assert mock_to_wire.call_count == 1
    assert mock_validate.call_count == 1


@mock.patch('jsonschema.validate')
def test_required(mock_validate):
    integer_spec = {
        'type': 'integer',
        'required': True,
    }
    assert 99 == marshal_primitive(integer_spec, 99)
    # 'required' has to be removed from the spec before calling
    # jsonschema.validate() for <see reasons in the code>
    spec_with_required_removed = integer_spec.copy()
    del spec_with_required_removed['required']
    assert mock_validate.call_args == mock.call(99, spec_with_required_removed)


def test_required_failure():
    integer_spec = {
        'type': 'integer',
        'required': True,
    }
    with pytest.raises(TypeError) as excinfo:
        marshal_primitive(integer_spec, None)
    assert 'is a required value' in str(excinfo.value)