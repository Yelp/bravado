import pytest

from bravado.mapping.model import compare, create_model_type


def test_true(user_model):
    assert compare(user_model, user_model)


def test_false(user_model, tag_model):
    assert not compare(user_model, tag_model)


def test_false_because_missing_dunder_dict(user_model):
    assert not compare(user_model, 'i am a string and do not have __dict__')
    assert not compare('i am a string and do not have __dict__', user_model)
