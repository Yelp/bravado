if True:
    import logging
    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)

import pytest

from bravado import client

@pytest.fixture
def petstore():
    return client.get_client('http://petstore.swagger.wordnik.com/v2/swagger.json')
