
import pytest

@pytest.mark.skip("Yelp/bravado 's testcases itself are failing")
def test_200_success(petstore):
    result = petstore.user.deleteUser(username='bozo').result()
    assert result is None


@pytest.mark.xfail(reason="Can't get this to 404")
def test_404_user_not_found(petstore):
    result = petstore.user.deleteUser(username='zzz').result()
    print(result)


@pytest.mark.xfail(reason="Can't get this to 400")
def test_400_invalid_username(petstore):
    result = petstore.user.deleteUser(username='aaa').result()
    print(result)
