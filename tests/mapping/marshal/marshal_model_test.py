import pytest

from bravado.mapping.marshal import marshal_model
from bravado.mapping.spec import Spec


def test_pet(petstore_dict):
    petstore_spec = Spec.from_dict(petstore_dict)
    Pet = petstore_spec.definitions['Pet']
    Category = petstore_spec.definitions['Category']
    Tag = petstore_spec.definitions['Tag']
    pet_spec = petstore_spec.spec_dict['definitions']['Pet']
    pet = Pet(
        id=1,
        name='Fido',
        status='sold',
        photoUrls=['wagtail.png', 'bark.png'],
        category=Category(id=200, name='friendly'),
        tags=[
            Tag(id=99, name='mini'),
            Tag(id=100, name='brown')
        ]
    )
    result = marshal_model(petstore_spec, pet_spec, pet)

    expected = {
        'id': 1,
        'name': 'Fido',
        'status': 'sold',
        'photoUrls': [
            'wagtail.png',
            'bark.png',
        ],
        'category': {
            'id': 200,
            'name': 'friendly',
        },
        'tags': [
            {
                'id': 99,
                'name': 'mini',
            },
            {
                'id': 100,
                'name': 'brown',
            },
        ]

    }
    assert expected == result


def test_attrs_set_to_None_are_absent_from_result(petstore_dict):
    # to recap: "required": ["name","photoUrls"]
    petstore_spec = Spec.from_dict(petstore_dict)
    Pet = petstore_spec.definitions['Pet']
    pet_spec = petstore_spec.spec_dict['definitions']['Pet']
    pet = Pet(
        id=1,
        name='Fido',
        status=None,
        photoUrls=['wagtail.png', 'bark.png'],
        category=None,
        tags=None
    )
    result = marshal_model(petstore_spec, pet_spec, pet)

    expected = {
        'id': 1,
        'name': 'Fido',
        'photoUrls': [
            'wagtail.png',
            'bark.png',
        ],
    }
    assert expected == result


def test_value_is_not_dict_like_raises_TypeError(petstore_dict):
    petstore_spec = Spec.from_dict(petstore_dict)
    pet_spec = petstore_spec.spec_dict['definitions']['Pet']
    with pytest.raises(TypeError) as excinfo:
        marshal_model(petstore_spec, pet_spec, 'i am not a dict')
    assert 'Expected model of type' in str(excinfo.value)
