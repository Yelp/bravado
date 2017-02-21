# -*- coding: utf-8 -*-

import socket
import threading
import time

import bottle

import pytest

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


@pytest.yield_fixture(scope='session')
def threaded_http_server():
    port = get_hopefully_free_port()
    thread = threading.Thread(
        target=bottle.run, kwargs={'host': 'localhost', 'port': port},
    )
    thread.daemon = True
    thread.start()
    time.sleep(2)
    yield port
