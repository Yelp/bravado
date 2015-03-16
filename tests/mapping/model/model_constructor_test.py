import pytest

from bravado.mapping.model import model_constructor


@pytest.fixture
def user_kwargs():
    return {
        'firstName': 'Darwin',
        'userStatus': 9,
        'id': 999L,
    }


def test_simple(user_spec, user, user_kwargs):
    model_constructor(user, user_spec, user_kwargs)
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


def test_additionalProperties_defaults_to_true_when_not_present(
        user_spec, user, user_kwargs):
    # verify exra kwargs are attached to the model as attributes when
    # additionalProperties is not present
    user_kwargs['foo'] = 'bar'
    model_constructor(user, user_spec, user_kwargs)
    assert user.foo == 'bar'
    assert 'foo' in dir(user)


def test_additionalProperties_true(user_spec, user, user_kwargs):
    # verify exra kwargs are attached to the model as attributes when
    # additionalProperties is True
    user_spec['additionalProperties'] = True
    user_kwargs['foo'] = 'bar'  # additional prop
    model_constructor(user, user_spec, user_kwargs)
    assert user.foo == 'bar'
    assert 'foo' in dir(user)


def test_additionalProperties_false(user_spec, user, user_kwargs):
    # verify exra kwargs are caught during model construction when
    # additionalProperties is False
    user_spec['additionalProperties'] = False
    user_kwargs['foo'] = 'bar'  # additional prop
    with pytest.raises(AttributeError) as excinfo:
        model_constructor(user, user_spec, user_kwargs)
    assert "does not have attributes for: ['foo']" in str(excinfo.value)
    assert not hasattr(user, 'foo')
    assert 'foo' not in dir(user)
