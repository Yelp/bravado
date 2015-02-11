import os
import simplejson as json

import pytest

from bravado.mapping.spec import Spec


@pytest.fixture
def empty_swagger_spec():
    return Spec(spec_dict={})


@pytest.fixture
def petstore_dict():
    my_dir = os.path.abspath(os.path.dirname(__file__))
    fpath = os.path.join(my_dir, '../../test-data/2.0/petstore/swagger.json')
    with open(fpath) as f:
        return json.loads(f.read())


@pytest.fixture
def petstore_spec(petstore_dict):
    return Spec(petstore_dict)
