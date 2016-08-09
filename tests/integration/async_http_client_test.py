# -*- coding: utf-8 -*-
import socket
import threading
import time
import unittest

import bottle
import pytest

from swaggerpy.async_http_client import AsynchronousHttpClient
from swaggerpy.exception import HTTPError
from swaggerpy.response import HTTPFuture


ROUTE_1_RESPONSE = b"HEY BUDDY"
ROUTE_2_RESPONSE = b"BYE BUDDY"


@bottle.route("/1")
def one():
    return ROUTE_1_RESPONSE


@bottle.route("/2")
def two():
    return ROUTE_2_RESPONSE


@bottle.route("/post", method="POST")
def post():
    name = bottle.request.forms.get("name")
    return 'Hello {name}! Have a snowman: ☃'.format(name=name)


def get_hopefully_free_port():
    s = socket.socket()
    s.bind(('', 0))
    port = s.getsockname()[1]
    s.close()
    return port


def launch_threaded_http_server(port):
    thread = threading.Thread(
        target=bottle.run, kwargs={'host': 'localhost', 'port': port},
    )
    thread.daemon = True
    thread.start()
    time.sleep(2)
    return thread


class TestServer(unittest.TestCase):

    def test_multiple_requests_against_async_client(self):
        port = get_hopefully_free_port()
        launch_threaded_http_server(port)

        client = AsynchronousHttpClient()

        request_one_params = {
            'method': b'GET',
            'headers': {},
            'url': "http://localhost:{0}/1".format(port),
            'params': {},
        }

        request_two_params = {
            'method': b'GET',
            'headers': {},
            'url': "http://localhost:{0}/2".format(port),
            'params': {},
        }

        eventual_one = client.start_request(request_one_params)
        eventual_two = client.start_request(request_two_params)
        resp_one = eventual_one.wait(timeout=1)
        resp_two = eventual_two.wait(timeout=1)

        self.assertEqual(resp_one.text, ROUTE_1_RESPONSE)
        self.assertEqual(resp_two.text, ROUTE_2_RESPONSE)

    def test_make_post_request(self):
        port = get_hopefully_free_port()
        launch_threaded_http_server(port)

        client = AsynchronousHttpClient()

        request_params = {
            'method': b'POST',
            'headers': {},
            'url': "http://localhost:{0}/post".format(port),
            'data': {'name': 'Matt'},
        }

        future = client.start_request(request_params)
        response = future.wait(timeout=1)

        self.assertEqual(
            response.text,
            u'Hello Matt! Have a snowman: ☃'.encode('utf-8'),
        )

    def test_erroring_request(self):
        port = get_hopefully_free_port()
        launch_threaded_http_server(port)

        client = AsynchronousHttpClient()

        params = {
            'method': b'GET',
            'headers': {},
            'url': 'http://localhost:{0}/404'.format(port),
            'params': {},
        }

        future = HTTPFuture(client, params, lambda x: x)
        with pytest.raises(HTTPError):
            future.result(timeout=1)
