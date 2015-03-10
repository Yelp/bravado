import mock
import pytest

from bravado.mapping.marshal import marshal_primitive


def test_success():
    integer_spec = {
        'type': 'integer'
    }
    assert 10 == marshal_primitive(integer_spec, 10)


@mock.patch('bravado.mapping.marshal.formatter.to_wire')
@mock.patch('bravado.mapping.marshal.validate_primitive')
def test_uses_default_and_skips_formatting_and_validation(
        mock_to_wire, mock_validate_primitive):
    integer_spec = {
        'type': 'integer',
        'default': 10,
    }
    assert 10 == marshal_primitive(integer_spec, None)
    assert mock_to_wire.call_count == 0
    assert mock_validate_primitive.call_count == 0


@mock.patch('bravado.mapping.marshal.formatter.to_wire', return_value=99)
@mock.patch('bravado.mapping.marshal.validate_primitive')
def test_skips_default(mock_to_wire, mock_validate_primitive):
    integer_spec = {
        'type': 'integer',
        'default': 10,
    }
    assert 99 == marshal_primitive(integer_spec, 99)
    assert mock_to_wire.call_count == 1
    assert mock_validate_primitive.call_count == 1


@mock.patch('bravado.mapping.marshal.validate_primitive')
def test_required(mock_validate_primitive):
    integer_spec = {
        'type': 'integer',
        'required': True,
    }
    assert 99 == marshal_primitive(integer_spec, 99)
    assert mock_validate_primitive.call_args == mock.call(integer_spec, 99)


def test_required_failure():
    integer_spec = {
        'type': 'integer',
        'required': True,
    }
    with pytest.raises(TypeError) as excinfo:
        marshal_primitive(integer_spec, None)
    assert 'is a required value' in str(excinfo.value)
