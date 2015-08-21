import pytest

from bravado_core.spec import Spec


@pytest.fixture
def request_dict():
    return {}


@pytest.fixture
def getPetById_spec(petstore_dict):
    return petstore_dict['paths']['/pet/{petId}']['get']


@pytest.fixture
def minimal_swagger_spec(getPetById_spec):
    spec_dict = {
        'paths': {
            '/pet/{petId}': {
                'get': getPetById_spec
            }
        }
    }
    return Spec(spec_dict)
