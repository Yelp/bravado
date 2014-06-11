#!/usr/bin/env python

"""Swagger client tests to validate resource_listing.

    "ResourceListing" > Resource > ResourceApi > ResourceOperation
"""

import httpretty
import unittest
import json

from swaggerpy.client import SwaggerClient
from swaggerpy.processors import SwaggerError


def register_urls(response):
    httpretty.register_uri(
        httpretty.GET, "http://localhost/api-docs",
        body=json.dumps(response))


# noinspection PyDocstring
class ResourceListingTest(unittest.TestCase):
    response = {"swaggerVersion": "1.2", "apis": [{"path": "/api"}]}

    @httpretty.activate
    def test_error_on_wrong_swagger_version(self):
        response = self.response.copy()
        response["swaggerVersion"] = "XYZ"
        register_urls(response)
        self.assertRaises(SwaggerError, SwaggerClient, u'http://localhost/api-docs')

    @httpretty.activate
    def test_error_on_missing_path_in_apis(self):
        response = self.response.copy()
        response['apis'] = [{}]
        register_urls(response)
        self.assertRaises(SwaggerError, SwaggerClient, u'http://localhost/api-docs')

    @httpretty.activate
    def test_error_on_missing_attr(self):
        def iterate_test(field):
            response = self.response.copy()
            response.pop(field)
            register_urls(response)
            self.assertRaises(SwaggerError, SwaggerClient, u'http://localhost/api-docs')
        [iterate_test(field) for field in ('swaggerVersion', 'apis')]

    @httpretty.activate
    def test_success_with_api_call(self):
        register_urls(self.response)
        httpretty.register_uri(
            httpretty.GET, "http://localhost/api-docs/api",
            body='{"swaggerVersion": "1.2", "basePath": "/", "apis":[]}')
        self.client = SwaggerClient(u'http://localhost/api-docs')
        self.assertNotEqual(None, self.client)

    def setUp(self):
        pass

if __name__ == '__main__':
    unittest.main()
