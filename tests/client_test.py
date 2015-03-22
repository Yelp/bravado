# -*- coding: utf-8 -*-
import datetime
import unittest

import httpretty
import requests
from mock import patch
import pytest

from bravado import client
from bravado.async_http_client import FidoHttpClient
from bravado.client import (
    SwaggerClient,
    SwaggerClientCache,
)


class SwaggerClientCacheTest(unittest.TestCase):

    def setUp(self):
        client.cache = None

    tearDown = setUp

    def test_is_stale_returns_true_after_ttl(self):
        with patch('bravado.client.SwaggerClient'):
            with patch('bravado.client.time.time', side_effect=[1]):
                client.get_client('test', ttl=10)
                assert client.cache.cache["('test',)[]"].is_stale(12)

    def test_is_stale_returns_false_before_ttl(self):
        with patch('bravado.client.SwaggerClient'):
            with patch('bravado.client.time.time', side_effect=[1]):
                client.get_client('test', ttl=10)
                assert not client.cache.cache["('test',)[]"].is_stale(11)

    def test_build_cached_item_with_proper_values(self):
        with patch('bravado.client.SwaggerClient.from_url') as mock:
            mock.return_value = 'foo'
            with patch('bravado.client.time.time',
                       side_effect=[1, 1]):
                cache = SwaggerClientCache()
                client_object = client.CacheEntry(
                    cache.build_client('test'), 3)
                self.assertEqual('foo', client_object.item)
                self.assertEqual(3, client_object.ttl)
                self.assertEqual(1, client_object.timestamp)

    def test_builds_client_if_not_present_in_cache(self):
        with patch('bravado.client.SwaggerClient.from_url') as mock:
            with patch('bravado.client.time.time', side_effect=[1]):
                client.get_client('foo')
                mock.assert_called_once_with('foo')

    def test_builds_client_if_present_in_cache_but_stale(self):
        with patch('bravado.client.time.time', side_effect=[2, 3]):
            client.cache = client.SwaggerClientCache()
            client.cache.cache['foo'] = client.CacheEntry('bar', 0, 1)
            with patch('bravado.client.SwaggerClient.from_url') as mock:
                client.get_client('foo')
                mock.assert_called_once_with('foo')

    def test_uses_the_cache_if_present_and_fresh(self):
        client.cache = client.SwaggerClientCache()
        client.cache.cache['foo'] = client.CacheEntry('bar', 2, 1)
        with patch('bravado.client.SwaggerClient') as mock:
            with patch('bravado.client.time.time', side_effect=[2]):
                client.get_client('foo')
                assert not mock.called

    @pytest.mark.xfail
    @patch('bravado.client.Loader', autospec=True)
    def test_cache_with_async_http_client(self, _):
        url = 'http://example.com/api-docs'
        swagger_client = client.get_client(
            url,
            http_client=FidoHttpClient())
        other = client.get_client(url, http_client=FidoHttpClient())
        assert swagger_client is other


class GetClientMethodTest(unittest.TestCase):

    def setUp(self):
        client.cache = None

    tearDown = setUp

    def test_get_client_gets_atleast_one_param(self):
        self.assertRaises(TypeError, client.get_client)

    def test_get_client_instantiates_new_factory_if_not_set(self):
        with patch.object(SwaggerClientCache, '__call__') as mock_method:
            mock_method.client.return_value = None
            client.get_client()
            self.assertTrue(client.cache is not None)

    def test_get_client_uses_instantiated_factory_second_time(self):
        with patch.object(SwaggerClientCache, '__call__') as mock_method:
            mock_method.client.return_value = None
            client.cache = SwaggerClientCache()
            prev_factory = client.cache
            client.get_client()
            self.assertTrue(prev_factory is client.cache)

    @pytest.mark.xfail
    def test_cache_of_a_json_dict(self):
        client.get_client({'swaggerVersion': '1.2', 'apis': []})
        self.assertTrue(
            repr(({'swaggerVersion': '1.2', 'apis': []},)) + "[]" in
            client.cache.cache)


@pytest.mark.xfail
class ClientTest(unittest.TestCase):

    def test_get_client_allows_json_dict(self):
        client_stub = client.get_client(self.resource_listing)
        self.assertTrue(isinstance(client_stub, client.SwaggerClient))

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
