from pprint import pprint
import pytest


def test_200_success(petstore):
    pet_api = petstore.pet
    future = pet_api.getPetById(petId=1)
    pet = future.result()
    print type(pet)
    pprint(pet)
    assert type(pet).__name__ == 'Pet'
    assert pet.name
    assert pet.status

    assert type(pet.category).__name__ == 'Category'
    assert pet.category.id is not None
    assert pet.category.name

    assert type(pet.photoUrls) == list
    assert pet.photoUrls

    assert type(pet.tags) == list
    assert pet.tags[0].id is not None
    assert pet.tags[0].name


@pytest.mark.xfail(reason="Petstore returns a 500 instead of a 404 - pet not found")
def test_404_pet_not_found(petstore):
    pet_api = petstore.pet
    future = pet_api.getPetById(petId=50)
    future.result()


@pytest.mark.xfail(reason="Don't know how to cause a 400")
def test_400_invalid_id_supplied(petstore):
    assert False