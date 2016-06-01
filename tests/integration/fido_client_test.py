# -*- coding: utf-8 -*-

import socket
import threading
import time

import bottle
import pytest
import six

from bravado.fido_client import FidoClient

ROUTE_1_RESPONSE = b"HEY BUDDY"
ROUTE_2_RESPONSE = b"BYE BUDDY"


@bottle.route("/1")
def one():
    return ROUTE_1_RESPONSE


@bottle.route("/2")
def two():
    return ROUTE_2_RESPONSE


@bottle.post('/double')
def double():
    x = bottle.request.params['number']
    return str(int(x) * 2)


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


class TestServer():

    @classmethod
    def setup_class(cls):
        cls.PORT = get_hopefully_free_port()
        launch_threaded_http_server(cls.PORT)
        cls.fido_client = FidoClient()

    def test_multiple_requests_against_fido_client(self):

        request_one_params = {
            'method': 'GET',
            'headers': {},
            'url': "http://localhost:{0}/1".format(self.PORT),
            'params': {},
        }

        request_two_params = {
            'method': 'GET',
            'headers': {},
            'url': "http://localhost:{0}/2".format(self.PORT),
            'params': {},
        }

        http_future_1 = self.fido_client.request(request_one_params)
        http_future_2 = self.fido_client.request(request_two_params)
        resp_one = http_future_1.result(timeout=1)
        resp_two = http_future_2.result(timeout=1)

        assert resp_one.text == ROUTE_1_RESPONSE
        assert resp_two.text == ROUTE_2_RESPONSE

    def test_post_request(self):

        request_args = {
            'method': 'POST',
            'headers': {},
            'url': "http://localhost:{0}/double".format(self.PORT),
            'data': {"number": 3},
        }

        http_future = self.fido_client.request(request_args)
        resp = http_future.result(timeout=1)

        assert resp.text == b'6'
