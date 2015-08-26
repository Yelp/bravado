import os

import simplejson as json
import pytest

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
