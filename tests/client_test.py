#!/usr/bin/env python

#
# Copyright (c) 2013, Digium, Inc.
#

"""Swagger client tests.
"""

import datetime
import json
import unittest

import httpretty
import requests
from mock import patch

from swaggerpy import client
from swaggerpy.http_client import SynchronousHttpClient
from swaggerpy.client import SwaggerClient, SwaggerClientFactory


class SwaggerClientFactoryTest(unittest.TestCase):
    """Test the proxy wrapper of SwaggerClient
    """

    def setUp(self):
        client.factory = None

    def test_is_stale_returns_true_after_timeout(self):
        with patch('swaggerpy.client.SwaggerClient'):
            with patch('swaggerpy.client.time.time', side_effect=[1]):
                client.get_client('test', timeout=10)
                self.assertTrue(client.factory.cache['test'].is_stale(12))

    def test_is_stale_returns_false_before_timeout(self):
        with patch('swaggerpy.client.SwaggerClient'):
            with patch('swaggerpy.client.time.time', side_effect=[1]):
                client.get_client('test', timeout=10)
                self.assertFalse(client.factory.cache['test'].is_stale(11))

    def test_build_cached_client_with_proper_values(self):
        with patch('swaggerpy.client.SwaggerClient') as mock:
            mock.return_value = 'foo'
            with patch('swaggerpy.client.time.time',
                       side_effect=[1, 1]):
                client_object = SwaggerClientFactory().build_cached_client(
                    'test', timeout=3)
                self.assertEqual('foo', client_object.swagger_client)
                self.assertEqual(3, client_object.timeout)
                self.assertEqual(1, client_object.timestamp)

    def test_builds_client_if_not_present_in_cache(self):
        with patch('swaggerpy.client.SwaggerClient') as mock:
            with patch('swaggerpy.client.time.time', side_effect=[1]):
                client.get_client('foo')
                mock.assert_called_once_with('foo')

    def test_builds_client_if_present_in_cache_but_stale(self):
        with patch('swaggerpy.client.time.time', side_effect=[2, 3]):
            client.factory = client.SwaggerClientFactory()
            client.factory.cache['foo'] = client.CachedClient('bar', 0, 1)
            with patch('swaggerpy.client.SwaggerClient') as mock:
                client.get_client('foo')
                mock.assert_called_once_with('foo')

    def test_uses_the_cache_if_present_and_fresh(self):
        client.factory = client.SwaggerClientFactory()
        client.factory.cache['foo'] = client.CachedClient('bar', 2, 1)
        with patch('swaggerpy.client.SwaggerClient') as mock:
            with patch('swaggerpy.client.time.time', side_effect=[2]):
                client.get_client('foo')
                assert not mock.called


class GetClientMethodTest(unittest.TestCase):

    def setUp(self):
        client.factory = None

    def test_get_client_gets_atleast_one_param(self):
        self.assertRaises(TypeError, client.get_client)

    def test_get_client_instantiates_new_factory_if_not_set(self):
        with patch.object(SwaggerClientFactory, '__call__') as mock_method:
            mock_method.client.return_value = None
            client.get_client()
            self.assertTrue(client.factory is not None)

    def test_get_client_uses_instantiated_factory_second_time(self):
        with patch.object(SwaggerClientFactory, '__call__') as mock_method:
            mock_method.client.return_value = None
            client.factory = SwaggerClientFactory()
            prev_factory = client.factory
            client.get_client()
            self.assertTrue(prev_factory is client.factory)


# noinspection PyDocstring
class ClientTest(unittest.TestCase):

    def test_get_client_allows_json_dict(self):
        client_stub = client.get_client(self.resource_listing)
        self.assertTrue(isinstance(client_stub, client.SwaggerClient))

    def test_serialization_of_json_dict(self):
        client.get_client({'swaggerVersion': '1.2', 'apis': []})
        self.assertTrue({'swaggerVersion': '1.2', 'apis': []} in
                        map(json.loads, client.factory.cache.keys()))

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
        self.uut = SwaggerClient(self.resource_listing,
                                 SynchronousHttpClient(headers={'foo': 'bar'}))
        httpretty.register_uri(
            httpretty.GET, "http://swagger.py/swagger-test/pet",
            body='[]')

        self.uut.pet.listPets().result()
        self.assertEqual('bar', httpretty.last_request().headers['foo'])

    @httpretty.activate
    def test_raise_with_wrapper(self):
        class MyException(Exception):
            pass
        self.uut = SwaggerClient(self.resource_listing, raise_with=MyException)
        httpretty.register_uri(
            httpretty.GET, "http://swagger.py/swagger-test/pet", status=500)
        self.assertRaises(MyException, self.uut.pet.listPets().result)

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
        self.uut = SwaggerClient(self.resource_listing)


if __name__ == '__main__':
    unittest.main()
