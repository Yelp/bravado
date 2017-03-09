# -*- coding: utf-8 -*-
def test_forwarded_to_delegate(petstore_client):
    expected = ['addPet', 'deletePet', 'findPetsByStatus', 'findPetsByTags',
                'getPetById', 'updatePet', 'updatePetWithForm', 'uploadFile']
    assert expected == dir(petstore_client.pet)
