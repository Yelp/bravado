from bravado.mapping.model import compare


def test_true(user):
    assert compare(user, user)


def test_false(user, tag_model):
    assert not compare(user, tag_model)


def test_false_because_missing_dunder_dict(user):
    assert not compare(user, 'i am a string and do not have __dict__')
    assert not compare('i am a string and do not have __dict__', user)
