import pytest

from bravado.client import CallableOperation
from bravado.client import ResourceDecorator


def test_resource_exists(petstore_client):
    assert type(petstore_client.pet) == ResourceDecorator
    assert type(petstore_client.pet.test) == ResourceDecorator
    assert type(petstore_client.pet.test.updatePet) == CallableOperation


def test_resource_not_found(petstore_client):
    with pytest.raises(AttributeError) as excinfo:
        petstore_client.foo
    assert 'foo not found' in str(excinfo.value)

    with pytest.raises(AttributeError) as excinfo:
        petstore_client.pet.test.error
