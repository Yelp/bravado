from bravado.mapping.exception import SwaggerMappingError
import pytest

from bravado.mapping.schema import get_spec_for_prop


@pytest.fixture
def address_spec():
    return {
        'type': 'object',
        'properties': {
            'number': {
                'type': 'number'
            },
            'street_name': {
                'type': 'string'
            },
            'street_type': {
                'type': 'string',
                'enum': [
                    'Street',
                    'Avenue',
                    'Boulevard']
            }
        }
    }


@pytest.fixture
def address():
    return {
        'number': 1600,
        'street_name': 'Pennsylvania',
        'street_type': 'Avenue'
    }


def test_declared_property(address_spec, address):
    expected_spec = address_spec['properties']['street_name']
    result = get_spec_for_prop(address_spec, address, 'street_name')
    assert expected_spec == result


def test_properties_and_additionalProperties_not_present(address):
    spec = {'type': 'object'}
    result = get_spec_for_prop(spec, address, 'street_name')
    assert result is None


def test_properties_not_present_and_additionalProperties_True(address):
    spec = {
        'type': 'object',
        'additionalProperties': True
    }
    result = get_spec_for_prop(spec, address, 'street_name')
    assert result is None


def test_properties_not_present_and_additionalProperties_False(address):
    spec = {
        'type': 'object',
        'additionalProperties': False
    }
    result = get_spec_for_prop(spec, address, 'street_name')
    assert result is None


def test_additionalProperties_with_spec(address_spec, address):
    address_spec['additionalProperties'] = {'type': 'string'}
    expected_spec = {'type': 'string'}
    # 'city' is not a declared property so it gets classified under
    # additionalProperties
    result = get_spec_for_prop(address_spec, address, 'city')
    assert expected_spec == result


def test_additionalProperties_not_dict_like(address_spec, address):
    address_spec['additionalProperties'] = 'i am not a dict'
    with pytest.raises(SwaggerMappingError) as excinfo:
        get_spec_for_prop(address_spec, address, 'city')
    assert "Don't know what to do" in str(excinfo.value)
