# -*- coding: utf-8 -*-
import datetime
import unittest

import httpretty
import requests
import pytest

from bravado.client import SwaggerClient


@pytest.mark.xfail
class SwaggerClientTest(unittest.TestCase):

    def test_from_dict(self):
        client_stub = SwaggerClient.from_dict(self.resource_listing)
        assert isinstance(client_stub, SwaggerClient)

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
    def test_headers(self):
        self.uut = SwaggerClient.from_resource_listing(self.resource_listing)
        httpretty.register_uri(
            httpretty.GET, "http://swagger.py/swagger-test/pet",
            body='[]')

        self.uut.pet.listPets(
            _request_options={'headers': {'foo': 'bar'}}).result()
        self.assertEqual('bar', httpretty.last_request().headers['foo'])

    @httpretty.activate
    def test_multiple_headers(self):
        self.uut = SwaggerClient.from_resource_listing(self.resource_listing)
        httpretty.register_uri(
            httpretty.GET, "http://swagger.py/swagger-test/pet",
            body='[]')

        self.uut.pet.listPets(
            _request_options={'headers': {'foo': 'bar', 'sweet': 'bike'}},
        ).result()
        self.assertEqual('bar', httpretty.last_request().headers['foo'])
        self.assertEqual('bike', httpretty.last_request().headers['sweet'])

    @httpretty.activate
    def test_get(self):
        httpretty.register_uri(
            httpretty.GET, "http://swagger.py/swagger-test/pet",
            body='[]')

        resp = self.uut.pet.listPets().result()
        self.assertEqual([], resp)

    @httpretty.activate
    def test_response_body_is_shown_in_error_message(self):
        httpretty.register_uri(
            httpretty.GET, "http://swagger.py/swagger-test/pet",
            body='{"success": false}', status=500)
        msg = '500 Server Error: Internal Server Error'

        try:
            self.uut.pet.listPets().result()
        except IOError as e:
            self.assertEqual(msg + ' : {"success": false}', e.args[0])

    @httpretty.activate
    def test_multiple(self):
        httpretty.register_uri(
            httpretty.GET, "http://swagger.py/swagger-test/pet/find",
            body='[]')

        resp = self.uut.pet.findPets(species=['cat', 'dog']).result()
        self.assertEqual([], resp)
        self.assertEqual({'species': ['cat', 'dog']},
                         httpretty.last_request().querystring)

    @httpretty.activate
    def test_post_and_optional_params(self):
        httpretty.register_uri(
            httpretty.POST, "http://swagger.py/swagger-test/pet",
            status=requests.codes.ok,
            body='"Spark is born"')

        resp = self.uut.pet.createPet(
            name='Sparky', birthday=datetime.date(2014, 1, 2)).result()
        self.assertEqual('Spark is born', resp)
        self.assertEqual({'name': ['Sparky'], 'birthday': ['2014-01-02']},
                         httpretty.last_request().querystring)
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
                                            },
                                            {
                                                "name": "birthday",
                                                "paramType": "query",
                                                "type": "string",
                                                "format": "date",
                                                "required": False
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
        self.uut = SwaggerClient.from_resource_listing(self.resource_listing)


if __name__ == '__main__':
    unittest.main()
