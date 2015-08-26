import pytest

from bravado.client import ResourceDecorator


def test_resource_exists(petstore_client):
    assert type(petstore_client.pet) == ResourceDecorator


def test_resource_not_found(petstore_client):
    with pytest.raises(AttributeError) as excinfo:
        petstore_client.foo
    assert 'foo not found' in str(excinfo.value)
