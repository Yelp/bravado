#!/usr/bin/env python

#
# Copyright (c) 2014, Yelp, Inc.
#

"""Swagger client tests to validate 'resource' declarations

A sample 'resource' is listed below.
{

    "apiVersion": "1.0.0",
    "swaggerVersion": "1.2",
    "basePath": "http://petstore.swagger.wordnik.com/api",
    "produces": [
        "application/json"
    ],
    "apis": [...]
}
"""

import json
import unittest

import httpretty

from swaggerpy.client import SwaggerClient, Resource, Operation
from swaggerpy.processors import SwaggerError


class ResourceTest(unittest.TestCase):
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
    def test_error_on_wrong_swagger_version(self):
        self.response["swaggerVersion"] = "XYZ"
        self.register_urls()
        self.assertRaises(SwaggerError, SwaggerClient, u'http://localhost/api-docs')

    @httpretty.activate
    def test_error_on_missing_attr(self):
        def iterate_test(field):
            self.response.pop(field)
            self.register_urls()
            self.assertRaises(SwaggerError, SwaggerClient, u'http://localhost/api-docs')
        [iterate_test(field) for field in ('swaggerVersion', 'basePath', 'apis')]

    # Use baesPath as api domain if it is '/' in the API declaration
    @httpretty.activate
    def test_correct_route_with_basePath_as_slash(self):
        httpretty.register_uri(
            httpretty.GET, "http://localhost/test_http?query=foo",
            body='[]')
        self.register_urls()
        resource = SwaggerClient(u'http://localhost/api-docs').api_test
        resp = resource.testHTTP(test_param="foo")()
        self.assertEqual([], resp)

    @httpretty.activate
    def test_setattrs_on_client_and_resource(self):
        self.register_urls()
        client = SwaggerClient(u'http://localhost/api-docs')
        self.assertTrue(isinstance(client.api_test, Resource))
        self.assertTrue(isinstance(client.api_test.testHTTP, Operation))

    # Use baesPath mentioned in the API declaration if it is not '/'
    @httpretty.activate
    def test_correct_route_with_basePath_no_slash(self):
        httpretty.register_uri(
            httpretty.GET, "http://localhost/lame/test/test_http?query=foo",
            body=u'""')
        self.response["basePath"] = "http://localhost/lame/test"
        self.register_urls()
        resource = SwaggerClient(u'http://localhost/api-docs').api_test
        resp = resource.testHTTP(test_param="foo")()
        self.assertEqual('', resp)


if __name__ == '__main__':
    unittest.main()
