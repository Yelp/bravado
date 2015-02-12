import pytest

from bravado.mapping.spec import Spec


@pytest.fixture
def empty_swagger_spec():
    return Spec(spec_dict={})

