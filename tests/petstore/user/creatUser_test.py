# -*- coding: utf-8 -*-
def test_200_success(petstore):
    User = petstore.get_model('User')
    user = User(
        id=1,
        username='bozo',
        firstName='Bozo',
        lastName='Smith',
        email='bozo@clown.com',
        password='letmein',
        phone='111-222-3333',
        userStatus=3,
    )
    result = petstore.user.createUser(body=user).result()
    assert result is None
