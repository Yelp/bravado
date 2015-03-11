from jsonschema.exceptions import ValidationError
import pytest

from bravado.mapping.validate import validate_object


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


def test_success(address_spec):
    address = {
        'number': 1000,
        'street_name': 'Main',
        'street_type': 'Street',
    }
    validate_object(address_spec, address)


def test_leaving_out_property_OK(address_spec):
    address = {
        'street_name': 'Main',
        'street_type': 'Street',
    }
    validate_object(address_spec, address)


def test_additional_property_OK(address_spec):
    address = {
        'number': 1000,
        'street_name': 'Main',
        'street_type': 'Street',
        'city': 'Swaggerville'
    }
    validate_object(address_spec, address)


def test_required_OK(address_spec):
    address_spec['required'] = ['number']
    address = {
        'street_name': 'Main',
        'street_type': 'Street',
    }
    with pytest.raises(ValidationError) as excinfo:
        validate_object(address_spec, address)
    assert 'is a required property' in str(excinfo.value)
