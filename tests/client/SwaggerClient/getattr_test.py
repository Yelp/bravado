# -*- coding: utf-8 -*-
import pytest

from bravado.client import ResourceDecorator, SwaggerClient


def test_resource_exists(petstore_client):
    assert type(petstore_client.pet) == ResourceDecorator


def test_resource_not_found(petstore_client):
    with pytest.raises(AttributeError) as excinfo:
        petstore_client.foo
    assert 'foo not found' in str(excinfo.value)


@pytest.fixture
def client_tags_with_spaces():
    return SwaggerClient.from_spec({
        'swagger': '2.0',
        'info': {
            'version': '',
            'title': 'API'
        },
        'paths': {
            '/ping': {
                'get': {
                    'operationId': 'ping',
                    'responses': {
                        '200': {
                            'description': 'ping'
                        }
                    },
                    'tags': [
                        'my tag'
                    ]
                }
            }
        }
    })


def test_get_resource(client_tags_with_spaces):
    assert type(client_tags_with_spaces.get_resource('my tag')) == ResourceDecorator
