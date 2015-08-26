def test_forwarded_to_delegate(petstore_client):
    expected = ['addPet', 'deletePet', 'findPetsByStatus', 'findPetsByTags',
                'getPetById', 'updatePet', 'updatePetWithForm']
    assert expected == dir(petstore_client.pet)
