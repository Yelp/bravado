# -*- coding: utf-8 -*-
import json
import threading
import time

import bottle
import ephemeral_port_reserve
import pytest
import umsgpack
from six.moves import urllib

from tests.conftest import petstore_dict
from tests.conftest import test_dir

ROUTE_1_RESPONSE = b"HEY BUDDY"
ROUTE_2_RESPONSE = b"BYE BUDDY"
MSGPACK_RESPONSE = {'answer': 42}


@bottle.get("/swagger.json")
def swagger_spec():
    return json.dumps(petstore_dict(test_dir()))


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


@bottle.route('/msgpack')
def msgpack():
    bottle.response.content_type = 'application/msgpack'
    return umsgpack.packb(MSGPACK_RESPONSE)


@bottle.get("/sleep")
def sleep_api():
    sec_to_sleep = float(bottle.request.GET.get('sec', '1'))
    time.sleep(sec_to_sleep)
    return sec_to_sleep


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
    server_address = 'http://localhost:{port}'.format(port=port)
    wait_unit_service_starts(server_address)
    yield server_address
