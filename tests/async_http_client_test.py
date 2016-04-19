#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
# Copyright (c) 2014, Yelp, Inc.
#

"""Unit tests for async http client related methods
Not Tested:
1) Callbacks triggered by twisted and crochet
2) Timeouts by crochet's wait()
"""

import unittest
from collections import namedtuple
from mock import patch, Mock

from crochet._eventloop import EventualResult
from twisted.internet.defer import Deferred
from twisted.web.http_headers import Headers

import swaggerpy.async_http_client
import swaggerpy.exception
import swaggerpy.http_client


class AsyncHttpClientTest(unittest.TestCase):

    def test_listify_headers(self):
        headers = {b'a': b'foo', b'b': [b'bar', 42]}
        resp = swaggerpy.async_http_client.listify_headers(headers)
        self.assertEqual([(b'A', [b'foo']), (b'B', [b'bar', 42])],
                         sorted(list(resp.getAllRawHeaders())))

    def test_success_AsyncHTTP_response(self):
        Response = namedtuple("MyResponse",
                              "version code phrase headers length deliverBody")
        with patch.object(
            swaggerpy.async_http_client.AsynchronousHttpClient,
            'fetch_deferred',
            return_value=Mock(
                autospec=EventualResult,
                _deferred=Mock(autospec=Deferred),
            ),
        ) as mock_Async:
            req = {
                'method': 'GET',
                'url': 'http://foo',
                'data': None,
                'headers': {'foo': 'bar'},
                'params': ''
            }
            mock_Async.return_value.wait.return_value = Response(
                1, 2, 3, 4, 5, 6)
            async_client = swaggerpy.async_http_client.AsynchronousHttpClient()
            eventual = async_client.start_request(req)
            resp = eventual.wait(timeout=5)
            self.assertEqual(2, resp.code)

    def test_url_encode_async_request(self):
        Response = namedtuple("MyResponse",
                              "version code phrase headers length deliverBody")
        with patch.object(
            swaggerpy.async_http_client.AsynchronousHttpClient,
            'fetch_deferred',
            return_value=Mock(
                autospec=EventualResult,
                _deferred=Mock(autospec=Deferred),
            ),
        ) as mock_fetch_deferred:
            req = {
                'method': 'GET',
                'url': 'http://foo',
                'data': None,
                'headers': {b'foo': b'bar'},
                'params': {'bar': u'酒場'},
            }
            mock_fetch_deferred.return_value.wait.return_value = Response(
                1, 2, 3, 4, 5, 6)

            async_client = swaggerpy.async_http_client.AsynchronousHttpClient()
            async_client.start_request(req)

            mock_fetch_deferred.assert_called_once_with(
                {
                    'headers': Headers({'foo': ['bar']}),
                    'method': b'GET',
                    'bodyProducer': None,
                    'uri': b'http://foo/?bar=%E9%85%92%E5%A0%B4',
                }
            )

    def test_start_request_with_only_url(self):
        url = b'http://example.com/api-docs'
        async_client = swaggerpy.async_http_client.AsynchronousHttpClient()
        # ugly mock, but this method runs in a twisted reactor which is
        # difficult to mock
        async_client.fetch_deferred = Mock()

        async_client.start_request(dict(url=url))

        async_client.fetch_deferred.assert_called_once_with({
            'headers': Headers({}),
            'method': b'GET',
            'bodyProducer': None,
            'uri': url,
        })


class HTTPBodyFetcherTest(unittest.TestCase):

    def setUp(self):
        self.http_body_fetcher = swaggerpy.async_http_client._HTTPBodyFetcher(
            'req', 'resp', Mock())

    def test_HTTP_body_fetcher_data_received(self):
        self.http_body_fetcher.dataReceived(b"helloWorld")
        self.assertEqual(b"helloWorld",
                         self.http_body_fetcher.buffer.getvalue())

    def test_success_HTTP_body_fetcher_connection_lost(self):
        response_str = 'swaggerpy.async_http_client.AsyncResponse'
        with patch(response_str) as mock_resp:
            self.http_body_fetcher.finished.callback.return_value = None
            reason = Mock(**{'check.return_value': True})
            self.http_body_fetcher.connectionLost(reason)
            mock_resp.assert_called_once_with('req', 'resp', b'')

    def test_error_HTTP_body_fetcher_connection_lost(self):
        errback = Mock()
        self.http_body_fetcher.finished.errback = errback
        reason = Mock(**{'check.return_value': False})
        self.http_body_fetcher.connectionLost(reason)
        errback.assert_called_once_with(reason)


class AsyncResponseTest(unittest.TestCase):

    def test_build_async_response(self):
        headers_orig = {b'a': b'foo', b'b': [b'bar', 42]}
        headers = swaggerpy.async_http_client.listify_headers(headers_orig)
        resp = Mock(**{'code': 200, 'headers': headers})
        req = Mock()
        async_resp = swaggerpy.async_http_client.AsyncResponse(
            req, resp, '{"valid":"json"}')
        self.assertEqual(200, async_resp.status_code)
        self.assertEqual(req, async_resp.request)
        self.assertEqual(
            {b'A': [b'foo'], b'B': [b'bar', 42]}, async_resp.headers,
        )
        self.assertEqual({"valid": "json"}, async_resp.json())

    def test_raise_for_status_client_error(self):
        headers = swaggerpy.async_http_client.listify_headers({})
        resp = Mock(**{'code': 400, 'headers': headers})
        async = swaggerpy.async_http_client.AsyncResponse(None, resp, None)
        try:
            async.raise_for_status()
        except swaggerpy.exception.HTTPError as e:
            self.assertEqual('400 Client Error', str(e))

    def test_raise_for_status_server_error(self):
        headers = swaggerpy.async_http_client.listify_headers({})
        resp = Mock(**{'code': 500, 'headers': headers})
        async = swaggerpy.async_http_client.AsyncResponse(None, resp, None)
        try:
            async.raise_for_status()
        except swaggerpy.exception.HTTPError as e:
            self.assertEqual('500 Server Error', str(e))
