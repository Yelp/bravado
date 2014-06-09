#!/usr/bin/env python

#
# Copyright (c) 2013, Digium, Inc.
#

"""Swagger client tests.
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
    trimmed_dict = {"swaggerVersion": "1.2", "apis": [{"path": "/api"}]}

    @httpretty.activate
    def test_wrong_swagger_version(self):
        trimmed_dict = self.trimmed_dict.copy()
        trimmed_dict["swaggerVersion"] = "XYZ"
        register_urls(trimmed_dict)
        self.assertRaises(AttributeError, SwaggerClient, u'http://localhost/api-docs')

    @httpretty.activate
    def test_missing_path_in_apis(self):
        trimmed_dict = self.trimmed_dict.copy()
        trimmed_dict['apis'] = [{}]
        register_urls(trimmed_dict)
        self.assertRaises(SwaggerError, SwaggerClient, u'http://localhost/api-docs')

    @httpretty.activate
    def test_missing_param(self):
        def iterate_test(field):
            trimmed_dict = self.trimmed_dict.copy()
            trimmed_dict.pop(field)
            register_urls(trimmed_dict)
            self.assertRaises(SwaggerError, SwaggerClient, u'http://localhost/api-docs')
        (iterate_test(field) for field in ('swaggerVersion', 'apis'))

    @httpretty.activate
    def test_call_api_declaration(self):
        register_urls(self.trimmed_dict)
        httpretty.register_uri(
            httpretty.GET, "http://localhost/api-docs/api",
            body='{"swaggerVersion": "1.2", "basePath": "/", "apis":[]}')
        self.client = SwaggerClient(u'http://localhost/api-docs')
        self.assertNotEqual(None, self.client)

    def setUp(self):
        pass

if __name__ == '__main__':
    unittest.main()
