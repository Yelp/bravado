# -*- coding: utf-8 -*-

import socket
import threading
import time
import unittest

import bottle
import pytest
import six

try:
    from bravado.fido_client import FidoClient
except ImportError:
    pass  # Tests will be skipped in py3

ROUTE_1_RESPONSE = "HEY BUDDY"
ROUTE_2_RESPONSE = "BYE BUDDY"


@bottle.route("/1")
def one():
    return ROUTE_1_RESPONSE


@bottle.route("/2")
def two():
    return ROUTE_2_RESPONSE


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


@pytest.mark.skipif(six.PY3, reason="twisted doesnt support py3 yet")
class TestServer(unittest.TestCase):

    def test_multiple_requests_against_fido_client(self):
        port = get_hopefully_free_port()
        launch_threaded_http_server(port)

        client = FidoClient()

        request_one_params = {
            'method': 'GET',
            'headers': {},
            'url': "http://localhost:{0}/1".format(port),
            'params': {},
        }

        request_two_params = {
            'method': 'GET',
            'headers': {},
            'url': "http://localhost:{0}/2".format(port),
            'params': {},
        }

        eventual_one = client.request(request_one_params)
        eventual_two = client.request(request_two_params)
        resp_one = eventual_one.result(timeout=1)
        resp_two = eventual_two.result(timeout=1)

        self.assertEqual(resp_one.text, ROUTE_1_RESPONSE)
        self.assertEqual(resp_two.text, ROUTE_2_RESPONSE)
