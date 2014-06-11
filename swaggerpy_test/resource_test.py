#!/usr/bin/env python

"""Swagger client tests to validate resource declarations

    ResourceListing > Resource > ResourceApi > ResourceOperation
"""

import httpretty
import unittest
import json

from swaggerpy.client import SwaggerClient, Resource, Operation
from swaggerpy.processors import SwaggerError


class ResourceTest(unittest.TestCase):

    parameter = {"paramType": "query", "name": "test_param", "type": "string"}
    operation = {"method": "GET", "nickname": "testHTTP", "type": "void", "parameters": [parameter]}
    api = {"path": "/test_http", "operations": [operation]}
    response = {"swaggerVersion": "1.2", "basePath": "/", "apis": [api]}

    def register_urls(self, response=response):
        httpretty.register_uri(
            httpretty.GET, "http://localhost/api-docs",
            body=json.dumps({"swaggerVersion": "1.2", "apis": [{"path": "/api_test"}]}))
        httpretty.register_uri(
            httpretty.GET, "http://localhost/api-docs/api_test",
            body=json.dumps(response))

    @httpretty.activate
    def test_error_on_wrong_swagger_version(self):
        response = self.response.copy()
        response["swaggerVersion"] = "XYZ"
        self.register_urls(response)
        self.assertRaises(SwaggerError, SwaggerClient, u'http://localhost/api-docs')

    @httpretty.activate
    def test_error_on_missing_attr(self):
        def iterate_test(field):
            response = self.response.copy()
            response.pop(field)
            self.register_urls(response)
            self.assertRaises(SwaggerError, SwaggerClient, u'http://localhost/api-docs')
        [iterate_test(field) for field in ('swaggerVersion', 'basePath', 'apis')]

    #Use baesPath as api domain if it is '/' in the API declaration
    @httpretty.activate
    def test_correct_route_with_basePath_as_slash(self):
        httpretty.register_uri(
            httpretty.GET, "http://localhost/test_http?query=foo",
            body='[]')
        self.register_urls()
        resource = SwaggerClient(u'http://localhost/api-docs').api_test
        resp = resource.testHTTP(test_param="foo")
        self.assertEqual(200, resp.status_code)
        self.assertEqual([], resp.json())

    @httpretty.activate
    def test_setattrs_on_client_and_resource(self):
        self.register_urls(self.response)
        client = SwaggerClient(u'http://localhost/api-docs')
        self.assertTrue(isinstance(client.api_test, Resource))
        self.assertTrue(isinstance(client.api_test.testHTTP, Operation))

    #Use baesPath mentioned in the API declaration if it is not '/'
    @httpretty.activate
    def test_correct_route_with_basePath_no_slash(self):
        httpretty.register_uri(
            httpretty.GET, "http://localhost/lame/test/test_http?query=foo",
            body=u'""')
        response = self.response.copy()
        response["basePath"] = "http://localhost/lame/test"
        self.register_urls(response)
        resource = SwaggerClient(u'http://localhost/api-docs').api_test
        resp = resource.testHTTP(test_param="foo")
        self.assertEqual(200, resp.status_code)
        self.assertEqual('', resp.json())

    def setUp(self):
        pass


if __name__ == '__main__':
    unittest.main()
