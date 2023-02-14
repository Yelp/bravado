# -*- coding: utf-8 -*-
import base64
import typing
import unittest

import httpretty
try:
    from unittest import mock
except ImportError:
    import mock
import pytest
import requests
from bravado_core.response import IncomingResponse

from bravado.requests_client import Authenticator
from bravado.requests_client import RequestsClient


class RequestsClientTestCase(unittest.TestCase):

    def _default_params(self):
        return {
            'method': 'GET',
            'url': 'http://swagger.py/client-test',
            'headers': {},
        }

    @httpretty.activate
    def test_simple_get(self):
        httpretty.register_uri(
            httpretty.GET, "http://swagger.py/client-test",
            body='expected')

        client = RequestsClient()
        params = self._default_params()
        params['params'] = {'foo': 'bar'}

        resp = typing.cast(IncomingResponse, client.request(params).result())

        self.assertEqual(200, resp.status_code)
        self.assertEqual('expected', resp.text)
        self.assertEqual({'foo': ['bar']},
                         httpretty.last_request().querystring)

    @httpretty.activate
    def test_unicode_to_utf8_encode_params(self):
        httpretty.register_uri(
            httpretty.GET, "http://swagger.py/client-test",
            body='expected')

        client = RequestsClient()
        params = self._default_params()
        params['params'] = {'foo': u'酒場'}

        resp = typing.cast(IncomingResponse, client.request(params).result())

        self.assertEqual(200, resp.status_code)
        self.assertEqual('expected', resp.text)
        self.assertEqual({'foo': [u'酒場']},
                         httpretty.last_request().querystring)

    @httpretty.activate
    def test_real_post(self):
        httpretty.register_uri(
            httpretty.POST, "http://swagger.py/client-test",
            body='expected', content_type='text/json')

        client = RequestsClient()
        params = self._default_params()
        params['data'] = {'foo': 'bar'}
        params['method'] = 'POST'

        resp = typing.cast(IncomingResponse, client.request(params).result())

        self.assertEqual(200, resp.status_code)
        self.assertEqual('expected', resp.text)

        self.assertEqual('application/x-www-form-urlencoded',
                         httpretty.last_request().headers['content-type'])
        self.assertEqual(b"foo=bar",
                         httpretty.last_request().body)

    @httpretty.activate
    def test_basic_auth(self):
        httpretty.register_uri(
            httpretty.GET, "http://swagger.py/client-test",
            body='expected')

        client = RequestsClient()
        client.set_basic_auth("swagger.py", 'unit', 'peekaboo')
        params = self._default_params()
        params['params'] = {'foo': 'bar'}

        resp = typing.cast(IncomingResponse, client.request(params).result())

        self.assertEqual(200, resp.status_code)
        self.assertEqual('expected', resp.text)
        self.assertEqual({'foo': ['bar']},
                         httpretty.last_request().querystring)
        self.assertEqual(
            'Basic %s' % base64.b64encode(b"unit:peekaboo").decode('utf-8'),
            httpretty.last_request().headers.get('Authorization'))

    @httpretty.activate
    def test_api_key(self):
        httpretty.register_uri(
            httpretty.GET, "http://swagger.py/client-test",
            body='expected')

        client = RequestsClient()
        client.set_api_key("swagger.py", 'abc123', param_name='test')
        params = self._default_params()
        params['params'] = {'foo': 'bar'}

        resp = typing.cast(IncomingResponse, client.request(params).result())

        self.assertEqual(200, resp.status_code)
        self.assertEqual('expected', resp.text)
        self.assertEqual({'foo': ['bar'], 'test': ['abc123']},
                         httpretty.last_request().querystring)
        self.assertEqual(None, httpretty.last_request().headers.get('test'))

    @httpretty.activate
    def test_api_key_header(self):
        httpretty.register_uri(
            httpretty.GET, "http://swagger.py/client-test",
            body='expected')

        client = RequestsClient()
        client.set_api_key("swagger.py", 'abc123', param_name='Key',
                           param_in='header')
        params = self._default_params()
        params['params'] = {'foo': 'bar'}

        resp = typing.cast(IncomingResponse, client.request(params).result())

        self.assertEqual(200, resp.status_code)
        self.assertEqual('expected', resp.text)
        self.assertEqual({'foo': ['bar']},
                         httpretty.last_request().querystring)
        self.assertEqual('abc123', httpretty.last_request().headers['Key'])

    @httpretty.activate
    def test_api_key_header_overwrite(self):
        httpretty.register_uri(
            httpretty.GET, "http://swagger.py/client-test",
            body='expected')

        client = RequestsClient()
        client.set_api_key("swagger.py", 'abc123', param_name='Key',
                           param_in='header')
        params = self._default_params()
        params['params'] = {'foo': 'bar'}
        params['headers'] = {'Key': 'def456'}

        resp = typing.cast(IncomingResponse, client.request(params).result())

        self.assertEqual(200, resp.status_code)
        self.assertEqual('expected', resp.text)
        self.assertEqual({'foo': ['bar']},
                         httpretty.last_request().querystring)
        self.assertEqual('def456', httpretty.last_request().headers['Key'])

    @httpretty.activate
    def test_auth_leak(self):
        httpretty.register_uri(
            httpretty.GET, "http://hackerz.py",
            body='expected')

        client = RequestsClient()
        client.set_basic_auth("swagger.py", 'unit', 'peekaboo')
        params = self._default_params()
        params['params'] = {'foo': 'bar'}
        params['url'] = 'http://hackerz.py'

        resp = typing.cast(IncomingResponse, client.request(params).result())

        self.assertEqual(200, resp.status_code)
        self.assertEqual('expected', resp.text)
        self.assertEqual({'foo': ['bar']},
                         httpretty.last_request().querystring)
        self.assertTrue(
            httpretty.last_request().headers.get('Authorization') is None)


class AuthenticatorTestCase(unittest.TestCase):

    def test_matches(self):
        authenticator = Authenticator("test.com:8080")
        self.assertTrue(authenticator.matches("https://test.com:8080/"))
        self.assertFalse(authenticator.matches("https://test.com:80/"))
        self.assertFalse(authenticator.matches("https://test.net:8080/"))


@pytest.fixture
def mock_session():
    return mock.create_autospec(requests.Session)


@pytest.fixture
def mock_request():
    return mock.create_autospec(
        requests.Request,
        method='GET',
        url='http://example.com',
        params={})


@pytest.mark.xfail(reason='Removed SynchronousEventual from http client')
class TestSynchronousEventual(object):

    def test_result(self, mock_session, mock_request):
        timeout = 20
        # sync_eventual = SynchronousEventual(mock_session, mock_request)
        # assert sync_eventual.result(timeout) == mock_session.send.return_value

        mock_session.send.assert_called_once_with(
            mock_session.prepare_request.return_value,
            timeout=timeout)

    def test_cancel(self, mock_session, mock_request):
        # sync_eventual = SynchronousEventual(mock_session, mock_request)
        # no-op cancel, test that is supports the interface
        # sync_eventual.cancel()
        pass
