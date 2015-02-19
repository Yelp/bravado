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
    assert dict == type(result)
    assert 1 == result['id']
    assert 'Fido' == result['name']
