from __future__ import print_function


def test_success(petstore):
    Pet = petstore.get_model('Pet')
    Category = petstore.get_model('Category')
    Tag = petstore.get_model('Tag')
    fido = Pet(
        id=99,
        name='fido',
        status='available',
        category=Category(id=101, name='dogz'),
        photoUrls=['http://fido.jpg'],
        tags=[Tag(id=102, name='friendly')])
    result = petstore.pet.addPet(body=fido).result()
    print(result)
