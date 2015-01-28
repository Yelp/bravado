from bravado.mapping.model import create_model_repr


def test_success(user_model):
    expected = "User(email='', firstName='', id=0L, lastName='', password='', phone='', userStatus=0, username='')"  # noqa
    assert expected == create_model_repr(user_model())
