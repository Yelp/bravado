#!/usr/bin/env python
# -*- coding: utf-8 -*-

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

from bravado.compat import json
import unittest

import httpretty
import pytest

from bravado.client import SwaggerClient, Resource, Operation


@pytest.mark.xfail(reason='Rewrite when Resource/Operation/Model for 2.0 done')
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
            body=json.dumps(
                {"swaggerVersion": "1.2", "apis": [{"path": "/api_test"}]}))
        httpretty.register_uri(
            httpretty.GET, "http://localhost/api-docs/api_test",
            body=json.dumps(self.response))

    # Use baesPath as api domain if it is '/' in the API declaration
    @httpretty.activate
    def test_correct_route_with_basePath_as_slash(self):
        httpretty.register_uri(
            httpretty.GET, "http://localhost/test_http?query=foo",
            body='[]')
        self.register_urls()
        resource = SwaggerClient.from_url(u'http://localhost/api-docs').api_test
        resp = resource.testHTTP(test_param="foo").result()
        self.assertEqual([], resp)

    @httpretty.activate
    def test_append_base_path_if_base_path_isnt_absolute(self):
        self.response["basePath"] = "/append"
        httpretty.register_uri(
            httpretty.GET, "http://localhost/append/test_http?",
            body='[]')
        self.register_urls()
        resource = SwaggerClient.from_url(u'http://localhost/api-docs').api_test
        resource.testHTTP(test_param="foo").result()
        self.assertEqual(["foo"],
                         httpretty.last_request().querystring['test_param'])

    @httpretty.activate
    def test_setattrs_on_client_and_resource(self):
        self.register_urls()
        client = SwaggerClient.from_url(u'http://localhost/api-docs')
        self.assertTrue(isinstance(client.api_test, Resource))
        self.assertTrue(isinstance(client.api_test.testHTTP, Operation))

    @httpretty.activate
    def test_headers_sendable_with_api_doc_request(self):
        self.register_urls()
        SwaggerClient.from_url(
            u'http://localhost/api-docs',
            request_options={'headers': {'foot': 'bart'}},
        )

        self.assertEqual(
            'bart',
            httpretty.last_request().headers.get('foot'),
        )

    @httpretty.activate
    def test_api_base_path_if_passed_is_always_used_as_base_path(self):
        httpretty.register_uri(
            httpretty.GET, "http://foo/test_http?", body='')
        self.response["basePath"] = "http://localhost"
        self.register_urls()
        resource = SwaggerClient.from_url(
            u'http://localhost/api-docs',
            api_base_path='http://foo').api_test
        resource.testHTTP(test_param="foo").result()
        self.assertEqual(["foo"],
                         httpretty.last_request().querystring['test_param'])

    # Use basePath mentioned in the API declaration only if
    # it does not start with '/' & no api_base_path is provided in the params
    @httpretty.activate
    def test_correct_route_with_basePath_no_slash(self):
        httpretty.register_uri(
            httpretty.GET, "http://localhost/lame/test/test_http?query=foo",
            body=u'""')
        self.response["basePath"] = "http://localhost/lame/test"
        self.register_urls()
        resource = SwaggerClient.from_url(u'http://localhost/api-docs').api_test
        resp = resource.testHTTP(test_param="foo").result()
        self.assertEqual('', resp)


if __name__ == '__main__':
    unittest.main()
