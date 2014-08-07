#!/usr/bin/env python

#
# Copyright (c) 2014, Yelp, Inc.
#

"""Swagger client tests to validate 'resource_listing'.

Sample 'resource_listing' this test intends to check is like:

{
    "apiVersion": "1.0.0",
    "swaggerVersion": "1.2",
    "apis": [
        {
            "path": "/pet",
            "description": "Operations about pets"
        },
        {
            "path": "/user",
            "description": "Operations about user"
        }
    ]
}
"""

import json
import unittest

import httpretty

from swaggerpy.client import SwaggerClient
from swaggerpy.http_client import SynchronousHttpClient
from swaggerpy.async_http_client import AsynchronousHttpClient
from swaggerpy.processors import SwaggerError


class ResourceListingTest(unittest.TestCase):
    def setUp(self):
        self.response = {
            "swaggerVersion": "1.2",
            "apis": [{
                "path": "/api"
            }]
        }

    def register_urls(self):
        httpretty.register_uri(
            httpretty.GET, "http://localhost/api-docs",
            body=json.dumps(self.response))

    @httpretty.activate
    def test_error_on_wrong_swagger_version(self):
        self.response["swaggerVersion"] = "XYZ"
        self.register_urls()
        self.assertRaises(SwaggerError, SwaggerClient,
                          u'http://localhost/api-docs')

    @httpretty.activate
    def test_error_on_missing_path_in_apis(self):
        self.response['apis'] = [{}]
        self.register_urls()
        self.assertRaises(SwaggerError, SwaggerClient,
                          u'http://localhost/api-docs')

    @httpretty.activate
    def test_error_on_missing_attr(self):
        def iterate_test(field):
            self.response.pop(field)
            self.register_urls()
            self.assertRaises(SwaggerError, SwaggerClient,
                              u'http://localhost/api-docs')
        [iterate_test(field) for field in ('swaggerVersion', 'apis')]

    @httpretty.activate
    def test_success_with_api_call(self):
        self.register_urls()
        httpretty.register_uri(
            httpretty.GET, "http://localhost/api-docs/api",
            body='{"swaggerVersion": "1.2", "basePath": "/", "apis":[]}')
        self.client = SwaggerClient(u'http://localhost/api-docs')
        self.assertNotEqual(None, self.client)

    @httpretty.activate
    def test_headers_present_when_loading_resource_through_Synchronous(self):
        self.response['apis'] = []
        self.register_urls()
        sync_http_client = SynchronousHttpClient(headers={'foo': 'bar'})
        SwaggerClient(u'http://localhost/api-docs',
                      http_client=sync_http_client)
        self.assertEqual('bar', httpretty.last_request().headers['foo'])

    @httpretty.activate
    def test_headers_present_when_loading_resource_through_Asynchronous(self):
        self.response['apis'] = []
        self.register_urls()
        async_http_client = AsynchronousHttpClient(headers={'foo': 'bar'})
        SwaggerClient(u'http://localhost/api-docs',
                      http_client=async_http_client)
        self.assertEqual('bar', httpretty.last_request().headers['foo'])

if __name__ == '__main__':
    unittest.main()
