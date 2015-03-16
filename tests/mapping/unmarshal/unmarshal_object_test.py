import pytest

from bravado.mapping.unmarshal import unmarshal_object
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


@pytest.fixture
def address():
    return {
        'number': 1600,
        'street_name': 'Pennsylvania',
        'street_type': 'Avenue'
    }


def test_properties(empty_swagger_spec, address_spec, address):
    expected_address = {
        'number': 1600,
        'street_name': 'Pennsylvania',
        'street_type': 'Avenue'
    }
    result = unmarshal_object(empty_swagger_spec, address_spec, address)
    assert expected_address == result


def test_array(empty_swagger_spec, address_spec):
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
    result = unmarshal_object(empty_swagger_spec, address_spec, address)
    assert result == address


def test_nested_object(empty_swagger_spec, address_spec):
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
    result = unmarshal_object(empty_swagger_spec, address_spec, address)
    assert result == address


def test_model(minimal_swagger_dict, address_spec):
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

    address_dict = {
        'number': 1600,
        'street_name': 'Pennsylvania',
        'street_type': 'Avenue',
        'location': {
            'longitude': 100.1,
            'latitude': 99.9,
        },
    }
    expected_address = {
        'number': 1600,
        'street_name': 'Pennsylvania',
        'street_type': 'Avenue',
        'location': Location(longitude=100.1, latitude=99.9),
    }

    address = unmarshal_object(swagger_spec, address_spec, address_dict)
    assert expected_address == address


def test_object_not_dict_like_raises_TypeError(
        empty_swagger_spec, address_spec):
    i_am_not_dict_like = 34
    with pytest.raises(TypeError) as excinfo:
        unmarshal_object(empty_swagger_spec, address_spec, i_am_not_dict_like)
    assert 'Expected dict' in str(excinfo.value)


def test_mising_properties_set_to_None(
        empty_swagger_spec, address_spec, address):
    del address['street_name']
    expected_address = {
        'number': 1600,
        'street_name': None,
        'street_type': 'Avenue'
    }
    result = unmarshal_object(empty_swagger_spec, address_spec, address)
    assert expected_address == result


def test_pass_through_additionalProperties_with_no_spec(
        empty_swagger_spec, address_spec, address):
    address_spec['additionalProperties'] = True
    address['city'] = 'Swaggerville'
    expected_address = {
        'number': 1600,
        'street_name': 'Pennsylvania',
        'street_type': 'Avenue',
        'city': 'Swaggerville',
    }
    result = unmarshal_object(empty_swagger_spec, address_spec, address)
    assert expected_address == result

