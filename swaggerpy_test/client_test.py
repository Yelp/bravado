#!/usr/bin/env python

#
# Copyright (c) 2013, Digium, Inc.
#

"""Swagger client tests.
"""

import time
import unittest
from mock import patch

import httpretty
import requests

from swaggerpy import client


class SwaggerClientTest(unittest.TestCase):
    """Test the proxy wrapper of SwaggerClient
    """

    def setUp(self):
        client.SWAGGER_SPEC_LIFETIME_S = 10

    def test_is_stale_returns_true_after_timeout(self):
        with patch('swaggerpy.client._SwaggerClient'):
            mocked_client = client.SwaggerClient()
            with patch('swaggerpy.client.time.time',
                       return_value=(time.time() + 11)):
                self.assertTrue(mocked_client._is_stale())

    def test_is_stale_returns_true_if_init_failed(self):
        with patch('swaggerpy.client._SwaggerClient',
                   side_effect=Exception()):
            mocked_client = client.SwaggerClient()
            self.assertEqual(None, mocked_client)
            self.assertTrue(mocked_client._is_stale())

    def test_is_stale_returns_false_before_timeout(self):
        with patch('swaggerpy.client._SwaggerClient'):
            mocked_client = client.SwaggerClient()
            with patch('swaggerpy.client.time.time',
                       return_value=(time.time() + 9)):
                self.assertFalse(mocked_client._is_stale())

    def test_refetch_of_swagger_client_if_stale(self):
        with patch('swaggerpy.client._SwaggerClient') as mock:
            with patch('swaggerpy.client.SwaggerClient._is_stale',
                       return_value=True):
                mocked_client = client.SwaggerClient()
                # On a random attr call, SwaggerClient should
                # again be fetched if stale.
                mocked_client.foo
                self.assertEqual(2, mock.call_count)

    def test_update_timestamp_updates_the_time(self):
        with patch('swaggerpy.client._SwaggerClient'):
            mocked_client = client.SwaggerClient()
            new_time = time.time()
            with patch('swaggerpy.client.time.time',
                       return_value=(new_time)):
                mocked_client._update_timestamp()
                self.assertEqual(new_time, mocked_client.timestamp)

    def test_assign_client_calls_ctor_of_core_swagger_client(self):
        with patch('swaggerpy.client._SwaggerClient') as mock:
            # __init__ will be called twice,
            # once in SwaggerClient(), then in _assign_client()
            client.SwaggerClient()._assign_client()
            self.assertEqual(2, mock.call_count)


# noinspection PyDocstring
class ClientTest(unittest.TestCase):

    @httpretty.activate
    def test_bad_operation(self):
        try:
            self.uut.pet.doesNotExist()
            self.fail("Expected attribute error")
        except AttributeError:
            pass

    @httpretty.activate
    def test_bad_param(self):
        try:
            self.uut.pet.listPets(doesNotExist='asdf')
            self.fail("Expected type error")
        except TypeError:
            pass

    @httpretty.activate
    def test_missing_required(self):
        try:
            self.uut.pet.createPet()
            self.fail("Expected type error")
        except TypeError:
            pass

    @httpretty.activate
    def test_get(self):
        httpretty.register_uri(
            httpretty.GET, "http://swagger.py/swagger-test/pet",
            body='[]')

        resp = self.uut.pet.listPets().result()
        self.assertEqual([], resp)

    @httpretty.activate
    def test_multiple(self):
        httpretty.register_uri(
            httpretty.GET, "http://swagger.py/swagger-test/pet/find",
            body='[]')

        resp = self.uut.pet.findPets(species=['cat', 'dog']).result()
        self.assertEqual([], resp)
        self.assertEqual({'species': ['cat,dog']},
                         httpretty.last_request().querystring)

    @httpretty.activate
    def test_post(self):
        httpretty.register_uri(
            httpretty.POST, "http://swagger.py/swagger-test/pet",
            status=requests.codes.ok,
            body='"Spark is born"')

        resp = self.uut.pet.createPet(name='Sparky').result()
        self.assertEqual('Spark is born', resp)
        self.assertEqual({'name': ['Sparky']},
                         httpretty.last_request().querystring)

    @httpretty.activate
    def test_delete(self):
        httpretty.register_uri(
            httpretty.DELETE, "http://swagger.py/swagger-test/pet/1234",
            status=requests.codes.no_content)

        resp = self.uut.pet.deletePet(petId=1234).result()
        self.assertEqual(None, resp)

    def setUp(self):
        # Default handlers for all swagger.py access
        self.resource_listing = {
            "swaggerVersion": "1.2",
            "basePath": "http://swagger.py/swagger-test",
            "apis": [
                {
                    "path": "/api-docs/pet.json",
                    "description": "Test loader when missing a file",
                    "api_declaration": {
                        "swaggerVersion": "1.2",
                        "basePath": "http://swagger.py/swagger-test",
                        "resourcePath": "/pet.json",
                        "apis": [
                            {
                                "path": "/pet",
                                "operations": [
                                    {
                                        "method": "GET",
                                        "nickname": "listPets",
                                        "type": "array",
                                        "items": {
                                                "type": "string"
                                        },
                                        "parameters": []
                                    },
                                    {
                                        "method": "POST",
                                        "nickname": "createPet",
                                        "type": "string",
                                        "parameters": [
                                            {
                                                "name": "name",
                                                "paramType": "query",
                                                "type": "string",
                                                "required": True
                                            }
                                        ]
                                    }
                                ]
                            },
                            {
                                "path": "/pet/find",
                                "operations": [
                                    {
                                        "method": "GET",
                                        "nickname": "findPets",
                                        "type": "array",
                                        "items": {
                                                "type": "string"
                                        },
                                        "parameters": [
                                            {
                                                "name": "species",
                                                "paramType": "query",
                                                "type": "array",
                                                "items": {
                                                    "type": "string"
                                                },
                                                "allowMultiple": True
                                            }
                                        ]
                                    }
                                ]
                            },
                            {
                                "path": "/pet/{petId}",
                                "operations": [
                                    {
                                        "method": "DELETE",
                                        "nickname": "deletePet",
                                        "type": "void",
                                        "parameters": [
                                            {
                                                "name": "petId",
                                                "type": "integer",
                                                "paramType": "path"
                                            }
                                        ]
                                    }
                                ]
                            }
                        ],
                        "models": {}
                    }
                }
            ]
        }
        self.uut = client.SwaggerClient(self.resource_listing)


if __name__ == '__main__':
    unittest.main()
