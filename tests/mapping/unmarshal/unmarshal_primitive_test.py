import pytest

from bravado.mapping.unmarshal import unmarshal_primitive


def test_success():
    integer_spec = {
        'type': 'integer'
    }
    assert 10 == unmarshal_primitive(integer_spec, 10)


def test_required_success():
    integer_spec = {
        'type': 'integer',
        'required': True,
    }
    assert 10 == unmarshal_primitive(integer_spec, 10)


def test_required_failure():
    integer_spec = {
        'type': 'integer',
        'required': True,
    }
    with pytest.raises(TypeError) as excinfo:
        unmarshal_primitive(integer_spec, None)
    assert 'is a required value' in str(excinfo.value)
