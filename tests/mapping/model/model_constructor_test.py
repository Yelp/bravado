import pytest

from bravado.mapping.model import model_constructor


def test_simple(user_spec, user):
    constructor_kwargs = {
        'firstName': 'Darwin',
        'userStatus': 9,
        'id': 999L,
    }
    model_constructor(user, user_spec, constructor_kwargs)
    assert user.firstName == 'Darwin'
    assert user.userStatus == 9
    assert user.id == 999L
    assert user.lastName is None
    assert user.email is None
    assert user.password is None


def test_empty_kwargs(user_spec, user):
    model_constructor(user, user_spec, {})
    assert user.firstName is None
    assert user.userStatus is None
    assert user.id is None
    assert user.lastName is None
    assert user.email is None
    assert user.password is None


def test_invalid_kwargs(user_spec, user):
    constructor_kwargs = {
        'firstName': 'Darwin',
        'userStatus': 9,
        'id': 999L,
        'foo': 'bar',  # should cause error
    }
    with pytest.raises(AttributeError) as excinfo:
        model_constructor(user, user_spec, constructor_kwargs)
    assert 'does not have attributes for' in str(excinfo.value)
    assert 'foo' in str(excinfo.value)
