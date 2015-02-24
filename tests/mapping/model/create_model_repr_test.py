from bravado.mapping.model import create_model_repr


def test_success(user):
    expected = "User(email=None, firstName=None, id=None, lastName=None, password=None, phone=None, userStatus=None, username=None)"  # noqa
    assert expected == create_model_repr(user)
