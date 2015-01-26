# -*- coding: utf-8 -*-
#
# Copyright (c) 2013, Digium, Inc.
# Copyright (c) 2014, Yelp, Inc.
#
import unittest

import httpretty
import pytest

from bravado.client import SwaggerClient


# noinspection PyDocstring
@pytest.mark.xfail(reason='Re-write when client ported over to Swagger 2.0')
class ClientTest(unittest.TestCase):

    # Pass body if available and send header as json
    @httpretty.activate
    def test_post_check_headers(self):
        body = {"id": "test_id"}
        httpretty.register_uri(
            httpretty.POST, "http://localhost/test_http?",
            body='[]', content_type='text/json')
        resp = self.client.simple1.createAsterikInfoHttp(body=body).result()
        self.assertEqual('application/json',
                         httpretty.last_request().headers['content-type'])
        self.assertEqual('{"id": "test_id"}',
                         httpretty.last_request().body)
        self.assertEqual([], resp)

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
            body=open('test-data/1.2/simple/resources.json', 'r').read())

        httpretty.register_uri(
            httpretty.GET, "http://localhost/api-docs/simple",
            body=open('test-data/1.2/simple/simple.json', 'r').read())

        httpretty.register_uri(
            httpretty.GET, "http://localhost/api-docs/simple1",
            body=open('test-data/1.2/simple/simple1.json', 'r').read())

        # Default handlers for all swagger.py access
        self.client = SwaggerClient.from_url(u'http://localhost/api-docs')


if __name__ == '__main__':
    unittest.main()
