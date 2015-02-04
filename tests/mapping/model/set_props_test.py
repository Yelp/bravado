import pytest

from bravado.mapping.model import set_props


def test_no_props_passed_to_constructor(user_model):
    set_props(user_model)
    assert user_model.firstName == ''   # str
    assert user_model.userStatus == 0   # int
    assert user_model.id == 0L          # long


def test_props_passed_to_constructor(user_model):
    props = {
        'firstName': 'Darwin',
        'userStatus': 9,
        'id': 999L,
    }
    set_props(user_model, **props)
    assert user_model.firstName == 'Darwin'
    assert user_model.userStatus == 9
    assert user_model.id == 999L


def test_extra_props_error(user_model):
    props = {'foo': 'bar'}
    with pytest.raises(AttributeError) as excinfo:
        set_props(user_model, **props)
    assert 'not defined' in str(excinfo.value)


def test_mixture_of_extra_props_and_valid_props_raises_error(user_model):
    props = {
        'firstName': 'Darwin',
        'foo': 'i am an invalid prop'
    }
    with pytest.raises(AttributeError) as excinfo:
        set_props(user_model, **props)
    assert 'not defined' in str(excinfo.value)
