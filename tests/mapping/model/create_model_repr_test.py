from bravado.mapping.model import create_model_repr


def test_success(user_model):
    repr = create_model_repr(user_model())
    expected = "User(username='', firstName='', lastName='', userStatus=0, email='', phone='', password='', id=0L)"  # noqa
    assert repr == expected
