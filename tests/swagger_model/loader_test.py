# -*- coding: utf-8 -*-
import pytest

from bravado.swagger_model import Loader


@pytest.fixture
def yaml_spec():
    return """swagger: '2.0'
info:
  version: 1.0.0
  title: Simple
paths:
  /ping:
    get:
      operationId: ping
      responses:
        200:
          description: pong"""


def test_load_yaml(yaml_spec):
    loader = Loader(None)
    result = loader.load_yaml(yaml_spec)

    assert result == {
        'swagger': '2.0',
        'info': {
            'version': '1.0.0',
            'title': 'Simple',
        },
        'paths': {
            '/ping': {
                'get': {
                    'operationId': 'ping',
                    'responses': {
                        '200': {
                            'description': 'pong',
                        },
                    },
                },
            },
        },
    }
