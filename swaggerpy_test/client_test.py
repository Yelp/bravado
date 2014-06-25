#!/usr/bin/env python

#
# Copyright (c) 2013, Digium, Inc.
#

"""Swagger client tests.
"""

import httpretty
import requests
import unittest

from swaggerpy.client import SwaggerClient


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

        resp = self.uut.pet.listPets()
        self.assertEqual(200, resp.status_code)
        self.assertEqual([], resp.json())

    @httpretty.activate
    def test_multiple(self):
        httpretty.register_uri(
            httpretty.GET, "http://swagger.py/swagger-test/pet/find",
            body='[]')

        resp = self.uut.pet.findPets(species=['cat', 'dog'])
        self.assertEqual(200, resp.status_code)
        self.assertEqual([], resp.json())
        self.assertEqual({'species': ['cat,dog']},
                         httpretty.last_request().querystring)

    @httpretty.activate
    def test_post(self):
        httpretty.register_uri(
            httpretty.POST, "http://swagger.py/swagger-test/pet",
            status=requests.codes.created,
            body='{"id": 1234, "name": "Sparky"}')

        resp = self.uut.pet.createPet(name='Sparky')
        self.assertEqual(requests.codes.created, resp.status_code)
        self.assertEqual({"id": 1234, "name": "Sparky"}, resp.json())
        self.assertEqual({'name': ['Sparky']},
                         httpretty.last_request().querystring)

    @httpretty.activate
    def test_delete(self):
        httpretty.register_uri(
            httpretty.DELETE, "http://swagger.py/swagger-test/pet/1234",
            status=requests.codes.no_content)

        resp = self.uut.pet.deletePet(petId=1234)
        self.assertEqual(requests.codes.no_content, resp.status_code)
        self.assertEqual('', resp.content)

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
                                        "type": "void",
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
                                                "type": "string",
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
                                                "type": "string",
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
        self.uut = SwaggerClient(self.resource_listing)


if __name__ == '__main__':
    unittest.main()
