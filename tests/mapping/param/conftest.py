import pytest

from bravado.mapping.spec import Spec


@pytest.fixture
def swagger_object():
    return Spec(spec_dict={})

