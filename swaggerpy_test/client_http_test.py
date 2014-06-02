#!/usr/bin/env python

#
# Copyright (c) 2013, Digium, Inc.
#

"""Swagger client tests.
"""

import httpretty
import unittest

from swaggerpy.client import SwaggerClient


# noinspection PyDocstring
class ClientTest(unittest.TestCase):

    #Use baesPath as api domain if it is '/' in the API declaration
    @httpretty.activate
    def test_get_check_basePath(self):
        httpretty.register_uri(
            httpretty.GET, "http://localhost/test_http?test_param=foo",
            body='[]')

        #simple1 has '/' in the API spec
        resource = self.client.simple1
        resp = resource.getAsteriskInfoHttp(test_param="foo")
        self.assertEqual(200, resp.status_code)
        self.assertEqual([], resp.json())

    #Use baesPath mentioned in the API declaration if it is not '/'
    @httpretty.activate
    def test_get_check_basePath_no_slash(self):
        httpretty.register_uri(
            httpretty.GET, "http://localhost/swagger/test/test?test_param=foo",
            body='[]')

        resp = self.client.simple.getAsteriskInfo(test_param="foo")
        self.assertEqual(200, resp.status_code)
        self.assertEqual([], resp.json())

    #Pass body if available and send header as json
    @httpretty.activate
    def test_post_check_headers(self):
        body = {"id":"test_id"}
        httpretty.register_uri(
            httpretty.POST, "http://localhost/test_http?",
            body='[]', content_type='text/json')
        resp = self.client.simple1.createAsterikInfoHttp(body=body)
        self.assertEqual('application/json',
                         httpretty.last_request().headers['content-type'])
        self.assertEqual('{"id": "test_id"}',
                         httpretty.last_request().body)
        self.assertEqual(200, resp.status_code)
        self.assertEqual([], resp.json())

    @httpretty.activate
    def test_bad_operation(self):
        try:
            self.client.simple.doesNotExist()
            self.fail("Expected attribute error")
        except AttributeError:
            pass

    @httpretty.activate
    def test_bad_param(self):
        try:
            self.client.simple.getAsteriskInfo(doesNotExist='asdf')
            self.fail("Expected type error")
        except TypeError:
            pass

    @httpretty.activate
    def test_missing_required(self):
        try:
            self.client.simple1.getAsteriskInfoHttp()
            self.fail("Expected type error")
        except TypeError:
            pass

    @httpretty.activate
    def setUp(self):
        httpretty.register_uri(
            httpretty.GET, "http://localhost/api-docs",
            body=open('test-data/1.2/simple/resources.json','r').read())

        httpretty.register_uri(
            httpretty.GET, "http://localhost/api-docs/simple.json",
            body=open('test-data/1.2/simple/simple.json','r').read())

        httpretty.register_uri(
            httpretty.GET, "http://localhost/api-docs/simple1.json",
            body=open('test-data/1.2/simple/simple1.json','r').read())

        # Default handlers for all swagger.py access
        self.client = SwaggerClient(u'http://localhost/api-docs')


if __name__ == '__main__':
    unittest.main()
