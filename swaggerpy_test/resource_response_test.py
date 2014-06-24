#!/usr/bin/env python

#
# Copyright (c) 2014, Yelp, Inc.
#

"""Swagger client tests to validate resource api response

The response is validated against Swagger spec specifications

Sample response:

    {'id': 42, 'name': 'spot', 'photoUrls': [], 'status': 'available'}

is validated against its type 'Pet' which is defined like so:

{
    "apiVersion": "1.0.0",
    "swaggerVersion": "1.2",
    "apis": [...],
    "models": {
        "Pet": {
            "id": "Pet",
            "required": [
                "id",
                "name"
            ],
            "properties": {
                "id": {
                    "type": "integer",
                    "format": "int64",
                    "description": "unique identifier for the pet",
                },
                "category": {
                    "$ref": "Category"
                },
                "name": {
                    "type": "string"
                },
                "photoUrls": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    }
                },
                "status": {
                    "type": "string",
                    "description": "pet status in the store",
                }
            }
        }
    }
}
"""

import json
import unittest
from datetime import datetime

import httpretty
from dateutil.tz import tzutc
from requests import HTTPError

from swaggerpy.client import SwaggerClient
from swaggerpy.processors import SwaggerError
from swaggerpy.response import HTTPFuture


class ResourceResponseTest(unittest.TestCase):
    def setUp(self):
        parameter = {
            "paramType": "query",
            "name": "test_param",
            "type": "string"
        }
        operation = {
            "method": "GET",
            "nickname": "testHTTP",
            "type": "void",
            "parameters": [parameter]
        }
        api = {
            "path": "/test_http",
            "operations": [operation]
        }
        self.response = {
            "swaggerVersion": "1.2",
            "basePath": "/",
            "apis": [api]
        }

    def register_urls(self):
        httpretty.register_uri(
            httpretty.GET, "http://localhost/api-docs",
            body=json.dumps({"swaggerVersion": "1.2", "apis": [{"path": "/api_test"}]}))
        httpretty.register_uri(
            httpretty.GET, "http://localhost/api-docs/api_test",
            body=json.dumps(self.response))

    @httpretty.activate
    def test_none_value_response_if_response_not_OK(self):
        self.register_urls()
        httpretty.register_uri(
            httpretty.GET, "http://localhost/test_http?test_param=foo",
            status=500)
        resource = SwaggerClient(u'http://localhost/api-docs').api_test
        self.assertRaises(HTTPError, resource.testHTTP(test_param="foo"))

    # Validate operation types against API response
    ###############################################

    @httpretty.activate
    def test_error_on_wrong_attr_type_in_operation_type(self):
        self.response["apis"][0]["operations"][0]["type"] = "WRONG_TYPE"
        self.register_urls()
        self.assertRaises(SwaggerError, SwaggerClient, u'http://localhost/api-docs')

    @httpretty.activate
    def test_success_on_correct_primitive_types_returned_by_operation(self):
        types = {
            'void': '[]',
            'string': '"test"',
            'integer': '42',
            'number': '3.4',
            'boolean': 'true'
        }
        for type_ in types:
            self.response["apis"][0]["operations"][0]["type"] = type_
            self.register_urls()
            httpretty.register_uri(
                httpretty.GET, "http://localhost/test_http?test_param=foo",
                body=types[type_])
            resource = SwaggerClient(u'http://localhost/api-docs').api_test
            resp = resource.testHTTP(test_param="foo")()
            self.assertEqual(json.loads(types[type_]), resp)

    @httpretty.activate
    def test_error_on_incorrect_primitive_types_returned(self):
        types = {
            'void': '"NOT_EMPTY"',
            'string': '42',
            'integer': '3.4',
            'number': '42',
            'boolean': '"NOT_BOOL"'
        }
        for type_ in types:
            self.response["apis"][0]["operations"][0]["type"] = type_
            self.register_urls()
            httpretty.register_uri(
                httpretty.GET, "http://localhost/test_http?test_param=foo",
                body=types[type_])
            resource = SwaggerClient(u'http://localhost/api-docs').api_test
            future = resource.testHTTP(test_param="foo")
            self.assertRaises(TypeError, future)

    # check array and datetime types
    @httpretty.activate
    def test_success_on_correct_array_type_returned_by_operation(self):
        self.response["apis"][0]["operations"][0]["type"] = "array"
        self.response["apis"][0]["operations"][0]["items"] = {
            "type": "string",
            "format": "date-time"
        }
        self.register_urls()
        httpretty.register_uri(
            httpretty.GET, "http://localhost/test_http?test_param=foo",
            body='["2014-06-10T23:49:54.728+0000"]')
        resource = SwaggerClient(u'http://localhost/api-docs').api_test
        resp = resource.testHTTP(test_param="foo")()
        self.assertEqual(resp, [datetime(2014, 6, 10, 23, 49, 54, 728000, tzinfo=tzutc())])

    @httpretty.activate
    def test_error_on_incorrect_array_type_returned(self):
        self.response["apis"][0]["operations"][0]["type"] = "array"
        self.response["apis"][0]["operations"][0]["items"] = {"type": "string"}
        self.register_urls()
        httpretty.register_uri(
            httpretty.GET, "http://localhost/test_http?test_param=foo",
            body="123.32")
        resource = SwaggerClient(u'http://localhost/api-docs').api_test
        future = resource.testHTTP(test_param="foo")
        self.assertRaises(TypeError, future)

    # Also test that /test_http? is not called when Future is returned for Sync
    @httpretty.activate
    def test_future_is_returned_from_swagger_client(self):
        self.register_urls()
        future = SwaggerClient(u'http://localhost/api-docs').api_test.testHTTP(test_param="a")
        self.assertTrue(isinstance(future, HTTPFuture))

    # TODO test timeout : delay/sleep in httpretty body doesn't work.
    @httpretty.activate
    def test_timeout_works_for_sync_http_client(self):
        pass


if __name__ == '__main__':
    unittest.main()
