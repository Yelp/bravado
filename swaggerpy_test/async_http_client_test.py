#!/usr/bin/env python

#
# Copyright (c) 2014, Yelp, Inc.
#

"""Unit tests for async http client related methods
Not Tested:
1) Callbacks triggered by twisted and crochet
2) Timeouts by crochet's wait()
"""

import json
import unittest
from collections import namedtuple
from mock import patch, Mock
from ordereddict import OrderedDict

import swaggerpy.async_http_client
import swaggerpy.exception
import swaggerpy.http_client


class AsyncHttpClientTest(unittest.TestCase):
    def setUp(self):
        self.req = {
            'method': 'GET',
            'url': 'foo',
            'data': {},
            'headers': {},
            'headers_forced': {},
            'params': ''}

    def test_stringify_body_converts_dict_to_str(self):
        request_params = {
            'headers': {'content-type': 'application/json'},
            'data': {'foo': 'bar', 'bar': 42}}
        swaggerpy.http_client.stringify_body(request_params)
        self.assertEqual({"foo": "bar", "bar": 42},
                         json.loads(request_params['data']))

    def test_stringify_body_ignores_data_if_header_content_type_not_json(self):
        request_params = {'headers': {}, 'data': 'foo'}
        swaggerpy.http_client.stringify_body(request_params)
        self.assertEqual('foo', request_params['data'])

    def test_stringify_body_ignores_data_if_header_not_present(self):
        request_params = {'data': 'foo'}
        swaggerpy.http_client.stringify_body(request_params)
        self.assertEqual('foo', request_params['data'])

    def test_stringify_body_ignores_data_if_already_str(self):
        request_params = {
            'headers': {'content-type': 'application/json'},
            'data': 'foo'}
        swaggerpy.http_client.stringify_body(request_params)
        self.assertEqual('foo', request_params['data'])

    def test_stringify_async_body_returns_file_producer(self):
        def_str = 'swaggerpy.http_client.stringify_body'
        with patch(def_str) as mock_stringify:
            with patch('swaggerpy.async_http_client.StringIO',
                       return_value='foo') as mock_stringIO:
                with patch('swaggerpy.async_http_client.FileBodyProducer',
                           return_value='mock_fbp') as mock_fbp:
                    resp = swaggerpy.async_http_client.stringify_body(
                        {'data': 42})

                    self.assertEqual('mock_fbp', resp)

                    mock_stringify.assert_called_once_with({'data': 42})
                    mock_stringIO.assert_called_once_with(42)
                    mock_fbp.assert_called_once_with('foo')

    def test_stringify_files_creates_correct_body_content(self):
        fake_file = Mock()
        fake_file.read.return_value = "contents"
        request = {'files': {'fake': fake_file},
                   'headers': {'content-type': 'tmp'}}
        with patch('swaggerpy.async_http_client.StringIO',
                   return_value='foo') as mock_stringIO:
            with patch('swaggerpy.async_http_client.FileBodyProducer'
                       ) as mock_fbp:
                with patch('swaggerpy.multipart_response.get_random_boundary',
                           return_value='zz'):
                    swaggerpy.async_http_client.stringify_body(request)

                    expected_contents = (
                        '--zz\r\nContent-Disposition: form-data; name=fake;' +
                        ' filename=fake\r\n\r\ncontents\r\n--zz--\r\n')
                    self.assertEqual('multipart/form-data; boundary=zz',
                                     request['headers']['content-type'])
                    mock_stringIO.assert_called_once_with(expected_contents)
                    mock_fbp.assert_called_once_with('foo')

    def test_stringify_files_creates_correct_form_content(self):
        request = {'data': OrderedDict([('id', 42), ('name', 'test')]),
                   'headers': {'content-type': swaggerpy.http_client.APP_FORM}}
        with patch('swaggerpy.async_http_client.StringIO',
                   return_value='foo') as mock_stringIO:
            with patch('swaggerpy.async_http_client.FileBodyProducer',
                       ) as mock_fbp:
                swaggerpy.async_http_client.stringify_body(request)

                expected_contents = ('id=42&name=test')
                mock_stringIO.assert_called_once_with(expected_contents)
                mock_fbp.assert_called_once_with('foo')

    def test_listify_headers(self):
        headers = {'a': 'foo', 'b': ['bar', 42]}
        resp = swaggerpy.async_http_client.listify_headers(headers)
        self.assertEqual([('A', ['foo']), ('B', ['bar', 42])],
                         sorted(list(resp.getAllRawHeaders())))

    def test_success_AsyncHTTP_response(self):
        Response = namedtuple("MyResponse",
                              "version code phrase headers length deliverBody")
        with patch.object(swaggerpy.async_http_client.AsynchronousHttpClient,
                          'fetch_deferred') as mock_Async:
            mock_Async.return_value.wait.return_value = Response(
                1, 2, 3, 4, 5, 6)
            async_client = swaggerpy.async_http_client.AsynchronousHttpClient(
                headers={'foo': 'bar'})
            async_client.setup(self.req)
            resp = async_client.wait(5)
            headers = async_client.request_params['headers']
            self.assertTrue(headers.hasHeader('foo'))
            self.assertEqual(2, resp.code)

    def test_headers_get_added_to_request(self):
        with patch.object(swaggerpy.async_http_client.AsynchronousHttpClient,
                          'fetch_deferred') as mock_Async:
            self.req['headers_forced'] = {'foo': 'bar'}
            mock_Async.return_value.wait.return_value = {}
            async_client = swaggerpy.async_http_client.AsynchronousHttpClient()
            async_client.setup(self.req)
            headers = async_client.request_params['headers']
            self.assertEqual(['bar'], headers.getRawHeaders('foo'))

    def test_headers_override_existing_headers_in_request(self):
        with patch.object(swaggerpy.async_http_client.AsynchronousHttpClient,
                          'fetch_deferred') as mock_Async:
            fake_file = Mock()
            fake_file.read.return_value = "contents"
            self.req.update({
                'files': {'fake': fake_file},
                'headers': {'content-type': 'tmp'},
                'headers_forced': {'content-type': 'bar'}})
            mock_Async.return_value.wait.return_value = {}
            async_client = swaggerpy.async_http_client.AsynchronousHttpClient()
            async_client.setup(self.req)
            headers = async_client.request_params['headers']
            self.assertEqual(['bar'], headers.getRawHeaders('content-type'))


class HTTPBodyFetcherTest(unittest.TestCase):

    def setUp(self):
        self.http_body_fetcher = swaggerpy.async_http_client._HTTPBodyFetcher(
            'req', 'resp', Mock())

    def test_HTTP_body_fetcher_data_received(self):
        self.http_body_fetcher.dataReceived("helloWorld")
        self.assertEqual("helloWorld",
                         self.http_body_fetcher.buffer.getvalue())

    def test_success_HTTP_body_fetcher_connection_lost(self):
        response_str = 'swaggerpy.async_http_client.AsyncResponse'
        with patch(response_str) as mock_resp:
            self.http_body_fetcher.finished.callback.return_value = None
            reason = Mock(**{'check.return_value': True})
            self.http_body_fetcher.connectionLost(reason)
            mock_resp.assert_called_once_with('req', 'resp', '')

    def test_error_HTTP_body_fetcher_connection_lost(self):
        errback = Mock()
        self.http_body_fetcher.finished.errback = errback
        reason = Mock(**{'check.return_value': False})
        self.http_body_fetcher.connectionLost(reason)
        errback.assert_called_once_with(reason)


class AsyncResponseTest(unittest.TestCase):

    def test_build_async_response(self):
        headers_orig = {'a': 'foo', 'b': ['bar', 42]}
        headers = swaggerpy.async_http_client.listify_headers(headers_orig)
        resp = Mock(**{'code': 200, 'headers': headers})
        req = Mock()
        async_resp = swaggerpy.async_http_client.AsyncResponse(
            req, resp, '{"valid":"json"}')
        self.assertEqual(200, async_resp.status_code)
        self.assertEqual(req, async_resp.request)
        self.assertEqual({'A': ['foo'], 'B': ['bar', 42]}, async_resp.headers)
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
