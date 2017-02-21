# -*- coding: utf-8 -*-
import pytest


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
    result = petstore.pet.updatePet(body=fido).result()
    assert result


@pytest.mark.xfail(reason="Don't know pet id to send in that will cause 404")
def test_404_pet_not_found():
    assert False


@pytest.mark.xfail(reason="Don't know pet id to send in that will cause 400")
def test_400_invalid_id():
    assert False


@pytest.mark.xfail(reason="Don't know pet id to send in that will cause 405")
def test_405_validation_exception():
    assert False
