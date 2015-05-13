import pytest


@pytest.mark.xfail(reason='Uh, the spec does not specify any parameters')
def test_200_success(petstore):
    result = petstore.user.logoutUser().result()
    assert result is None
