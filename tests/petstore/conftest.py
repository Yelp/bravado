import pytest

from bravado.client import SwaggerClient

# TODO: remove
if False:
    import logging
    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)


@pytest.fixture
def petstore():
    return SwaggerClient.from_url('http://petstore.swagger.io/v2/swagger.json')
