#!/usr/bin/env python
import base64

import unittest
import httpretty

from swaggerpy.http_client import SynchronousHttpClient


# noinspection PyDocstring
class SynchronousClientTestCase(unittest.TestCase):
    @httpretty.activate
    def test_simple_get(self):
        httpretty.register_uri(
            httpretty.GET, "http://swagger.py/client-test",
            body='expected')

        uut = SynchronousHttpClient()
        resp = uut.request('GET', "http://swagger.py/client-test",
                           params={'foo': 'bar'})
        self.assertEqual(200, resp.status_code)
        self.assertEqual('expected', resp.text)
        self.assertEqual({'foo': ['bar']},
                         httpretty.last_request().querystring)

    @httpretty.activate
    def test_real_post(self):
        httpretty.register_uri(
            httpretty.POST, "http://swagger.py/client-test",
            body='expected', content_type='text/json')

        uut = SynchronousHttpClient()
        resp = uut.request('POST', "http://swagger.py/client-test",
                           data={'foo': 'bar'})
        self.assertEqual(200, resp.status_code)
        self.assertEqual('expected', resp.text)
        self.assertEqual('application/x-www-form-urlencoded',
                         httpretty.last_request().headers['content-type'])
        self.assertEqual("foo=bar",
                         httpretty.last_request().body)

    @httpretty.activate
    def test_basic_auth(self):
        httpretty.register_uri(
            httpretty.GET, "http://swagger.py/client-test",
            body='expected')

        uut = SynchronousHttpClient()
        uut.set_basic_auth("swagger.py", 'unit', 'peekaboo')
        resp = uut.request('GET', "http://swagger.py/client-test",
                           params={'foo': 'bar'})
        self.assertEqual(200, resp.status_code)
        self.assertEqual('expected', resp.text)
        self.assertEqual({'foo': ['bar']},
                         httpretty.last_request().querystring)
        self.assertEqual('Basic %s' % base64.b64encode("unit:peekaboo"),
                         httpretty.last_request().headers.get('Authorization'))

    @httpretty.activate
    def test_api_key(self):
        httpretty.register_uri(
            httpretty.GET, "http://swagger.py/client-test",
            body='expected')

        uut = SynchronousHttpClient()
        uut.set_api_key("swagger.py",
                        'abc123', param_name='test')
        resp = uut.request('GET', "http://swagger.py/client-test",
                           params={'foo': 'bar'})
        self.assertEqual(200, resp.status_code)
        self.assertEqual('expected', resp.text)
        self.assertEqual({'foo': ['bar'], 'test': ['abc123']},
                         httpretty.last_request().querystring)

    @httpretty.activate
    def test_auth_leak(self):
        httpretty.register_uri(
            httpretty.GET, "http://hackerz.py",
            body='expected')

        uut = SynchronousHttpClient()
        uut.set_basic_auth("swagger.py", 'unit', 'peekaboo')
        resp = uut.request('GET', "http://hackerz.py",
                           params={'foo': 'bar'})
        self.assertEqual(200, resp.status_code)
        self.assertEqual('expected', resp.text)
        self.assertEqual({'foo': ['bar']},
                         httpretty.last_request().querystring)
        self.assertIsNone(
            httpretty.last_request().headers.get('Authorization'))


if __name__ == '__main__':
    unittest.main()
