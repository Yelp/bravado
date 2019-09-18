


def test_success(petstore):
    inventory = petstore.store.getInventory().result()
    assert dict == type(inventory)
    assert inventory
    print(inventory)
