# -*- coding: utf-8 -*-
import datetime
import tempfile
import unittest

import httpretty
import mock
import pytest
import requests

from bravado.client import SwaggerClient
from bravado.config import CONFIG_DEFAULTS


@pytest.fixture
def mock_spec():
    with mock.patch('bravado.client.Spec') as _mock:
        yield _mock


def test_remove_bravado_configs(mock_spec, processed_default_config):
    config = CONFIG_DEFAULTS.copy()
    config['validate_swagger_spec'] = False  # bravado_core config

    SwaggerClient.from_spec({}, config=config)

    mock_spec.from_dict.assert_called_once_with(
        {},  # spec_dict
        None,  # spec_url
        mock.ANY,  # http_client
        {
            'bravado': processed_default_config,
            'validate_swagger_spec': False,
        },  # config
    )


def test_also_return_response(mock_spec):
    with mock.patch('bravado.client.SwaggerClient.__init__') as mock_init:
        mock_init.return_value = None
        SwaggerClient.from_spec({}, config={'also_return_response': True})

    mock_init.assert_called_once_with(
        mock_spec.from_dict.return_value,
        also_return_response=True,
    )


@pytest.mark.xfail
class SwaggerClientTest(unittest.TestCase):

    def test_from_spec(self):
        client_stub = SwaggerClient.from_spec(self.resource_listing)
        assert isinstance(client_stub, SwaggerClient)

    @httpretty.activate
    def test_bad_operation(self):
        try:
            self.uut.pet.doesNotExist()  # type: ignore
            self.fail("Expected attribute error")
        except AttributeError:
            pass

    @httpretty.activate
    def test_bad_param(self):
        try:
            self.uut.pet.listPets(doesNotExist='asdf')  # type: ignore
            self.fail("Expected type error")
        except TypeError:
            pass

    @httpretty.activate
    def test_missing_required(self):
        try:
            self.uut.pet.createPet()  # type: ignore
            self.fail("Expected type error")
        except TypeError:
            pass

    @httpretty.activate
    def test_headers(self):
        self.uut = SwaggerClient.from_spec(self.resource_listing)
        httpretty.register_uri(
            httpretty.GET, "http://swagger.py/swagger-test/pet",
            body='[]')

        self.uut.pet.listPets(
            _request_options={'headers': {'foo': 'bar'}}).result()
        self.assertEqual('bar', httpretty.last_request().headers['foo'])

    @httpretty.activate
    def test_multiple_headers(self):
        self.uut = SwaggerClient.from_spec(self.resource_listing)
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
    def test_post_binary_data(self):
        httpretty.register_uri(
            httpretty.POST, 'http://swagger.py/swagger-test/pet/1234/vaccine',
            status=requests.codes.no_content)

        temporary_file = tempfile.TemporaryFile()
        temporary_file.write('\xff\xd8')
        temporary_file.seek(0)

        resp = self.uut.pet.postVaccine(
            vaccineFile=temporary_file, petId=1234).result()
        self.assertEqual(None, resp)

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
            u"swaggerVersion": u"1.2",
            u"basePath": u"http://swagger.py/swagger-test",
            u"apis": [
                {
                    u"path": u"/api-docs/pet.json",
                    u"description": u"Test loader when missing a file",
                    u"api_declaration": {
                        u"swaggerVersion": u"1.2",
                        u"basePath": u"http://swagger.py/swagger-test",
                        u"resourcePath": u"/pet.json",
                        u"apis": [
                            {
                                u"path": u"/pet",
                                u"operations": [
                                    {
                                        u"method": u"GET",
                                        u"nickname": u"listPets",
                                        u"type": u"array",
                                        u"items": {
                                            u"type": u"string"
                                        },
                                        u"parameters": []
                                    },
                                    {
                                        u"method": u"POST",
                                        u"nickname": u"createPet",
                                        u"type": u"string",
                                        u"parameters": [
                                            {
                                                u"name": u"name",
                                                u"paramType": u"query",
                                                u"type": u"string",
                                                u"required": True
                                            },
                                            {
                                                u"name": u"birthday",
                                                u"paramType": u"query",
                                                u"type": u"string",
                                                u"format": u"date",
                                                u"required": False
                                            }
                                        ]
                                    }
                                ]
                            },
                            {
                                u"path": u"/pet/find",
                                u"operations": [
                                    {
                                        u"method": u"GET",
                                        u"nickname": u"findPets",
                                        u"type": u"array",
                                        u"items": {
                                            u"type": u"string"
                                        },
                                        u"parameters": [
                                            {
                                                u"name": u"species",
                                                u"paramType": u"query",
                                                u"type": u"string",
                                                u"allowMultiple": True
                                            }
                                        ]
                                    }
                                ]
                            },
                            {
                                u"path": u"/pet/{petId}",
                                u"operations": [
                                    {
                                        u"method": u"DELETE",
                                        u"nickname": u"deletePet",
                                        u"type": u"void",
                                        u"parameters": [
                                            {
                                                u"name": u"petId",
                                                u"type": u"integer",
                                                u"paramType": u"path"
                                            }
                                        ]
                                    }
                                ]
                            },
                            {
                                u"path": u"/pet/{petId}/vaccine",
                                u"operations": [
                                    {
                                        u"method": u"POST",
                                        u"nickname": u"postVaccine",
                                        u"type": u"void",
                                        u"parameters": [
                                            {
                                                u"name": u"petId",
                                                u"type": u"integer",
                                                u"paramType": u"path"
                                            },
                                            {
                                                u"name": u"vaccineFile",
                                                u"type": u"File",
                                                u"paramType": u"form"
                                            }
                                        ]
                                    }
                                ]
                            }
                        ],
                        u"models": {}
                    }
                }
            ]
        }
        self.uut = SwaggerClient.from_spec(self.resource_listing)


if __name__ == '__main__':
    unittest.main()
