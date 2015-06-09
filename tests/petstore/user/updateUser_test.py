from __future__ import print_function
import pytest


def test_200_success(petstore):
    User = petstore.get_model('User')
    user = User(
        id=1,
        username='bozo',
        firstName='Bozo',
        lastName='TheClown',
        email='bozo@clown.com',
        password='newpassword',
        phone='111-222-3333',
        userStatus=2,
    )
    result = petstore.user.updateUser(username='bozo', body=user).result()
    assert result is None


@pytest.mark.xfail(reason='Broken on server side - blindly succeeds')
def test_404_user_not_found(petstore):
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
    result = petstore.user.updateUser(
        username='i_dont_exist', body=user).result()
    print(result)


@pytest.mark.xfail(reason='Broken on server side - blindly succeeds')
def test_400_invalid_username(petstore):
    assert False
