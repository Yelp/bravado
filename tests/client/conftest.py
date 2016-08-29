import os

from bravado.compat import json
import pytest

from bravado.client import Spec
from bravado.client import SwaggerClient


@pytest.fixture
def petstore_dict():
    my_dir = os.path.abspath(os.path.dirname(__file__))
    fpath = os.path.join(my_dir, '../../test-data/2.0/petstore/swagger.json')
    with open(fpath) as f:
        return json.loads(f.read())


@pytest.fixture
def petstore_client(petstore_dict):
    return SwaggerClient.from_spec(petstore_dict)


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
        },
        'securityDefinitions': {
            'api_key': {
                'type': 'apiKey',
                'name': 'api_key',
                'in': 'header',
            },
        },
    }
    spec = Spec(spec_dict)
    spec.api_url = 'http://localhost/swagger.json'
    return spec
