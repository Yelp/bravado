import pytest

@pytest.mark.skip("Yelp/bravado 's testcases itself are failing")
def test_success(petstore):
    inventory = petstore.store.getInventory().result()
    assert dict == type(inventory)
    assert inventory
    print(inventory)
