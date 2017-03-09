# -*- coding: utf-8 -*-
import threading
import time

import bottle
import ephemeral_port_reserve
import pytest
from six.moves import urllib

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


def wait_unit_service_starts(url, timeout=10):
    start = time.time()
    while time.time() < start + timeout:
        try:
            urllib.request.urlopen(url, timeout=2)
        except urllib.error.HTTPError:
            return
        except urllib.error.URLError:
            time.sleep(0.1)


@pytest.yield_fixture(scope='session')
def threaded_http_server():
    port = ephemeral_port_reserve.reserve()
    thread = threading.Thread(
        target=bottle.run, kwargs={'host': 'localhost', 'port': port},
    )
    thread.daemon = True
    thread.start()
    wait_unit_service_starts('http://localhost:{port}'.format(port=port))
    yield port
