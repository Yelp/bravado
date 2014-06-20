#!/usr/bin/env python

"""Swagger client tests to validate resource apis

ResourceListing > Resource > "ResourceApi" > ResourceOperation
"""

import httpretty
import unittest
import json
import copy

from swaggerpy.client import SwaggerClient
from swaggerpy.processors import SwaggerError


class ResourceApiTest(unittest.TestCase):
    parameter = {"paramType": "query", "name": "test_param", "type": "string"}
    operation = {"method": "GET", "nickname": "testHTTP", "type": "void", "parameters": [parameter]}
    api = {"path": "/test_http", "operations": [operation]}
    response = {"swaggerVersion": "1.2", "basePath": "/", "apis": [api]}

    def register_urls(self, response):
        httpretty.register_uri(
            httpretty.GET, "http://localhost/api-docs",
            body=json.dumps({"swaggerVersion": "1.2", "apis": [{"path": "/api_test"}]}))
        httpretty.register_uri(
            httpretty.GET, "http://localhost/api-docs/api_test",
            body=json.dumps(response))

    @httpretty.activate
    def test_error_on_missing_attr(self):
        def iterate_test(field):
            response = copy.deepcopy(self.response)
            response["apis"][0].pop(field)
            self.register_urls(response)
            self.assertRaises(SwaggerError, SwaggerClient, u'http://localhost/api-docs')
        [iterate_test(field) for field in ('path', 'operations')]

    def setUp(self):
        pass


if __name__ == '__main__':
    unittest.main()
