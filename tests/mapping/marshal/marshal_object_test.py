import pytest

from bravado.mapping.marshal import marshal_object
from bravado.mapping.spec import Spec


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


def test_object_with_properties(empty_swagger_spec, address_spec):
    address = {
        'number': 1600,
        'street_name': 'Pennsylvania',
        'street_type': 'Avenue'
    }
    result = marshal_object(empty_swagger_spec, address_spec, address)
    assert address == result


def test_object_with_array(empty_swagger_spec, address_spec):
    tags_spec = {
        'type': 'array',
        'items': {
            'type': 'string'
        }
    }
    address_spec['properties']['tags'] = tags_spec
    address = {
        'number': 1600,
        'street_name': 'Pennsylvania',
        'street_type': 'Avenue',
        'tags': [
            'home',
            'best place on earth',
            'cul de sac'
        ],
    }
    result = marshal_object(empty_swagger_spec, address_spec, address)
    assert result == address


def test_object_with_nested_object(empty_swagger_spec, address_spec):
    location_spec = {
        'type': 'object',
        'properties': {
            'longitude': {
                'type': 'number'
            },
            'latitude': {
                'type': 'number'
            },
        }
    }
    address_spec['properties']['location'] = location_spec
    address = {
        'number': 1600,
        'street_name': 'Pennsylvania',
        'street_type': 'Avenue',
        'location': {
            'longitude': 100.1,
            'latitude': 99.9,
        },
    }
    result = marshal_object(empty_swagger_spec, address_spec, address)
    assert result == address


def test_object_with_model(minimal_swagger_dict, address_spec):
    location_spec = {
        'type': 'object',
        'properties': {
            'longitude': {
                'type': 'number'
            },
            'latitude': {
                'type': 'number'
            },
        }
    }
    minimal_swagger_dict['definitions']['Location'] = location_spec
    swagger_spec = Spec.from_dict(minimal_swagger_dict)
    address_spec['properties']['location'] = \
        swagger_spec.spec_dict['definitions']['Location']
    Location = swagger_spec.definitions['Location']
    address = {
        'number': 1600,
        'street_name': 'Pennsylvania',
        'street_type': 'Avenue',
        'location': Location(longitude=100.1, latitude=99.9),
    }

    expected_address = {
        'number': 1600,
        'street_name': 'Pennsylvania',
        'street_type': 'Avenue',
        'location': {
            'longitude': 100.1,
            'latitude': 99.9,
        }
    }

    result = marshal_object(swagger_spec, address_spec, address)
    assert expected_address == result
