import copy

from bravado.mapping.unmarshal import unmarshal_array
from bravado.mapping.spec import Spec


def test_primitive_array(empty_swagger_spec):
    int_array_spec = {
        'type': 'array',
        'items': {
            'type': 'integer',
        }
    }
    result = unmarshal_array(empty_swagger_spec, int_array_spec, [1, 2, 3])
    assert [1, 2, 3] == result


def test_empty_array(empty_swagger_spec):
    int_array_spec = {
        'type': 'array',
        'items': {
            'type': 'integer',
        }
    }
    result = unmarshal_array(empty_swagger_spec, int_array_spec, [])
    assert [] == result


def test_array_of_array(empty_swagger_spec):
    array_of_array_spec = {
        'type': 'array',
        'items': {
            'type': 'array',
            'items': {
                'type': 'string',
            }
        }
    }
    input = [
        ['one'],
        ['two', 'three'],
        ['four', 'five', 'six']
    ]
    expected = copy.deepcopy(input)
    result = unmarshal_array(empty_swagger_spec, array_of_array_spec, input)
    assert expected == result


def test_array_of_objects(empty_swagger_spec):
    array_of_addresses_spec = {
        'type': 'array',
        'items': {
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
    }
    input = [
        {
            'number': 1600,
            'street_name': 'Pennsylvania',
            'street_type': 'Avenue'
        },
        {
            'number': 1700,
            'street_name': 'Main',
            'street_type': 'Street'
        },
        {
            'number': 1800,
            'street_name': 'Yelpy',
            'street_type': 'Boulevard'
        },
    ]
    expected = copy.deepcopy(input)
    result = unmarshal_array(empty_swagger_spec, array_of_addresses_spec, input)
    assert expected == result


def test_array_of_models(petstore_dict):
    petstore_spec = Spec.from_dict(petstore_dict)
    Pet = petstore_spec.definitions['Pet']
    Category = petstore_spec.definitions['Category']
    Tag = petstore_spec.definitions['Tag']

    array_of_pets_spec = {
        'type': 'array',
        'items': petstore_spec.spec_dict['definitions']['Pet']
    }

    fido_dict = {
        'id': 1,
        'name': 'Fido',
        'status': 'sold',
        'photoUrls': ['wagtail.png', 'bark.png'],
        'category': {
            'id': 200,
            'name': 'friendly',
        },
        'tags': [
            {
                'id': '99',
                'name': 'mini',
            },
            {
                'id': 100,
                'name': 'brown'
            }
        ],
    }

    pet_dicts = [fido_dict]
    pets = unmarshal_array(petstore_spec, array_of_pets_spec, pet_dicts)
    assert list == type(pets)
    assert 1 == len(pets)
    fido = pets[0]
    assert Pet == type(fido)
    assert Category == type(fido.category)
    assert Tag == type(fido.tags[0])
