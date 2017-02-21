# -*- coding: utf-8 -*-
from __future__ import print_function

import pytest


def test_200_success(petstore):
    order = petstore.store.getOrderById(orderId='1').result()
    assert petstore.get_model('Order') == type(order)


@pytest.mark.xfail(reason='Currently returning a 500 instead of a 404')
def test_404_order_not_found(petstore):
    order = petstore.store.getOrderById(orderId='7').result()
    print(order)


@pytest.mark.xfail(reason='Currently returning a 500 instead of a 404')
def test_400_invalid_id_supplied(petstore):
    order = petstore.store.getOrderById(orderId='@').result()
    print(order)
