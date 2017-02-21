# -*- coding: utf-8 -*-
from __future__ import print_function


def test_success(petstore):
    inventory = petstore.store.getInventory().result()
    assert dict == type(inventory)
    assert inventory
    print(inventory)
