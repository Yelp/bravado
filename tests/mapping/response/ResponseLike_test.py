import pytest

from bravado.mapping.response import ResponseLike


def test_required_attr_returned():

    class CompliantResponse(ResponseLike):

        def __init__(self):
            self.status_code = 99

    r = CompliantResponse()
    assert 99 == r.status_code


def test_missing_required_attr_throws_NotImplementedError():

    class NonCompliantResponse(ResponseLike):
        pass

    r = NonCompliantResponse()
    with pytest.raises(NotImplementedError) as excinfo:
        r.status_code
    assert 'forgot to implement' in str(excinfo.value)


def test_any_other_attr_throws_AttributeError():

    class UnrelatedReponse(ResponseLike):
        pass

    r = UnrelatedReponse()
    with pytest.raises(AttributeError):
        r.foo
