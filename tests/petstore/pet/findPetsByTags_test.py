import pytest


@pytest.mark.xfail(reason="Blows up with a 500 no matter what")
def test_200_success(petstore):
    pets = petstore.pet.findPetsByTags(tags=['string']).result()
    assert pets
    for pet in pets:
        assert type(pet).__name__ == 'Pet'
        assert pet.status == 'sold'


@pytest.mark.xfail(reason="Don't know how to cause a 400")
def test_400_invalid_tag_value(petstore):
    assert False
