#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
# Copyright (c) 2014, Yelp, Inc.
#

"""Unit tests for fido http client related methods
Not Tested:
1) Callbacks triggered by twisted and crochet
2) Timeouts by crochet's wait()
"""
import unittest
from collections import namedtuple
from mock import patch, Mock

import pytest
import six

try:
    import bravado.fido_client
except ImportError:
    pass  # Tests will be skipped in py3

from bravado.http_client import APP_FORM
import bravado.exception


@pytest.mark.skipif(
    six.PY3,
    reason="Fido client is not usable in py3 until twisted supports it",
)
class FidoHttpClientTest(unittest.TestCase):

    def test_stringify_fido_body_returns_file_producer(self):
        def_str = 'bravado.fido_client.param_stringify_body'
        with patch(def_str) as mock_stringify:
            mock_stringify.return_value = '42'
            body = {'data': 42, 'headers': {}}
            resp = bravado.fido_client.stringify_body(body)

            self.assertEqual('42', resp)

            mock_stringify.assert_called_once_with(body['data'])

    def test_stringify_files_creates_correct_body_content(self):
        fake_file = Mock()
        fake_file.read.return_value = "contents"
        request = {'files': {'fake': fake_file},
                   'headers': {'content-type': 'tmp'}}
        with patch('bravado.multipart_response.get_random_boundary',
                   return_value='zz'):
            resp = bravado.fido_client.stringify_body(request)

            expected_contents = (
                '--zz\r\nContent-Disposition: form-data; name=fake;' +
                ' filename=fake\r\n\r\ncontents\r\n--zz--\r\n')
            self.assertEqual('multipart/form-data; boundary=zz',
                             request['headers']['content-type'])
            self.assertEqual(expected_contents, resp)

    def test_stringify_files_creates_correct_form_content(self):
        request = {'data': {'id': 42, 'name': 'test'},
                   'headers': {'content-type': APP_FORM}}
        resp = bravado.fido_client.stringify_body(request)

        self.assertEqual(
            six.moves.urllib.parse.parse_qs('id=42&name=test'),
            six.moves.urllib.parse.parse_qs(resp),
        )

    def test_url_encode_FidoHTTP_response(self):
        Response = namedtuple("MyResponse",
                              "version code phrase headers length deliverBody")
        req = {
            'method': 'GET',
            'url': 'foo',
            'data': None,
            'headers': {'foo': 'bar'},
            'params': {'bar': u'酒場'},
        }
        fido_client = bravado.fido_client.FidoClient()
        with patch('fido.fetch') as mock_fido:
            mock_fido.return_value.result.return_value = Response(
                1, 2, 3, 4, 5, 6)
            eventual = fido_client.request(req)
            resp = eventual.result(timeout=5)
            self.assertEqual(2, resp.status_code)
        mock_fido.assert_called_once_with('foo?bar=%E9%85%92%E5%A0%B4',
                                          body=None, headers={'foo': 'bar'},
                                          method='GET')

    def test_start_request_with_only_url(self):
        url = 'http://example.com/api-docs'
        fido_client = bravado.fido_client.FidoClient()
        # ugly mock, but this method runs in a twisted reactor which is
        # difficult to mock
        fido_client.fetch_deferred = Mock()

        with patch('fido.fetch') as mock_fetch:
            fido_client.request(dict(url=url))

        mock_fetch.assert_called_once_with(
            '{0}?'.format(url), body='', headers={}, method='GET')
