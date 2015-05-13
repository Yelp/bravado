import pytest


def test_200_success(petstore):
    Order = petstore.get_model('Order')
    order = Order(id=1, petId=1, quantity=3)
    result = petstore.store.placeOrder(body=order).result()
    assert Order == type(result)


@pytest.mark.xfail(reason='Uh, how to you make an order invalid?')
def test_400_invalid_order(petstore):
    assert False
