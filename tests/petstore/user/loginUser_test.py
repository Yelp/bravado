from __future__ import print_function
import pytest


@pytest.mark.xfail(reason='Raw string in response instead of json. Spec needs to be fixed')  # noqa
def test_200_success(petstore):
    result = petstore.user.loginUser(
        username='bozo', password='letmein').result()
    print(result)

    # operation says that is produces:
    #
    # produces: [
    #     "application/json",
    #     "application/xml"
    # ],
    #
    # But the resonse contains only raw text:
    #
    # logged in user session:1423503862492
    #
    # This is an error in the spec


@pytest.mark.xfail(reason="Don't know user/pass to induce failure")
def test_400_invalid_username_or_password(petstore):
    assert False
