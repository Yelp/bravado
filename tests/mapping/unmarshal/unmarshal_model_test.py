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

    assert Pet == type(pet)
    assert 1 == pet.id
    assert 'Fido' == pet.name
    assert 'sold' == pet.status
    assert ['wagtail.png', 'bark.png'] == pet.photoUrls
    assert Category == type(pet.category)
    assert 200 == pet.category.id
    assert 'friendly' == pet.category.name
    assert list == type(pet.tags)
    assert 2 == len(pet.tags)
    assert Tag == type(pet.tags[0])
    assert 99 == pet.tags[0].id
    assert 'mini' == pet.tags[0].name
    assert Tag == type(pet.tags[1])
    assert 100 == pet.tags[1].id
    assert 'brown' == pet.tags[1].name
