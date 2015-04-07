import pytest

from bravado.mapping.request import RequestLike


def test_required_attr_returned():

    class CompliantRequest(RequestLike):

        def __init__(self):
            self.path = {'biz_id': 99}

    r = CompliantRequest()
    assert 99 == r.path.get('biz_id')


def test_missing_required_attr_throws_NotImplementedError():

    class NonCompliantRequest(RequestLike):
        pass

    r = NonCompliantRequest()
    with pytest.raises(NotImplementedError) as excinfo:
        r.path
    assert 'forgot to implement' in str(excinfo.value)


def test_any_other_attr_throws_AttributeError():

    class UnrelatedRequest(RequestLike):
        pass

    r = UnrelatedRequest()
    with pytest.raises(AttributeError):
        r.foo
