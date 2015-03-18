import pytest

from bravado.mapping.unmarshal import unmarshal_model
from bravado.mapping.spec import Spec


def test_pet(petstore_dict):
    # Covers:
    #   - model with primitives properties
    #   - model with an array
    #   - model with a nested model
    petstore_spec = Spec.from_dict(petstore_dict)
    Pet = petstore_spec.definitions['Pet']
    Category = petstore_spec.definitions['Category']
    Tag = petstore_spec.definitions['Tag']
    pet_spec = petstore_spec.spec_dict['definitions']['Pet']
    pet_dict = {
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
                'id': 99,
                'name': 'mini'
            },
            {
                'id': 100,
                'name': 'brown'
            }
        ],
    }

    pet = unmarshal_model(petstore_spec, pet_spec, pet_dict)

    assert isinstance(pet, Pet)
    assert 1 == pet.id
    assert 'Fido' == pet.name
    assert 'sold' == pet.status
    assert ['wagtail.png', 'bark.png'] == pet.photoUrls
    assert isinstance(pet.category, Category)
    assert 200 == pet.category.id
    assert 'friendly' == pet.category.name
    assert isinstance(pet.tags, list)
    assert 2 == len(pet.tags)
    assert isinstance(pet.tags[0], Tag)
    assert 99 == pet.tags[0].id
    assert 'mini' == pet.tags[0].name
    assert isinstance(pet.tags[1], Tag)
    assert 100 == pet.tags[1].id
    assert 'brown' == pet.tags[1].name


def test_Nones_are_reintroduced_for_declared_properties_that_are_not_present(
        petstore_dict):
    petstore_spec = Spec.from_dict(petstore_dict)
    Pet = petstore_spec.definitions['Pet']
    Tag = petstore_spec.definitions['Tag']
    pet_spec = petstore_spec.spec_dict['definitions']['Pet']

    # Deleting "status" and "category" from pet_dict means that should still be
    # attrs on Pet with a None value after unmarshaling
    pet_dict = {
        'id': 1,
        'name': 'Fido',
        'photoUrls': ['wagtail.png', 'bark.png'],
        'tags': [
            {
                'id': 99,
                'name': 'mini'
            },
            {
                'id': 100,
                'name': 'brown'
            }
        ],
    }

    pet = unmarshal_model(petstore_spec, pet_spec, pet_dict)

    assert isinstance(pet, Pet)
    assert 1 == pet.id
    assert 'Fido' == pet.name
    assert pet.status is None
    assert ['wagtail.png', 'bark.png'] == pet.photoUrls
    assert pet.category is None
    assert isinstance(pet.tags, list)
    assert 2 == len(pet.tags)
    assert isinstance(pet.tags[0], Tag)
    assert 99 == pet.tags[0].id
    assert 'mini' == pet.tags[0].name
    assert isinstance(pet.tags[1], Tag)
    assert 100 == pet.tags[1].id
    assert 'brown' == pet.tags[1].name


def test_value_is_not_dict_like_raises_TypeError(petstore_dict):
    petstore_spec = Spec.from_dict(petstore_dict)
    pet_spec = petstore_spec.spec_dict['definitions']['Pet']
    with pytest.raises(TypeError) as excinfo:
        unmarshal_model(petstore_spec, pet_spec, 'i am not a dict')
    assert 'Expected type to be dict' in str(excinfo.value)
