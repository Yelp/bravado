# -*- coding: utf-8 -*-
import pickle
import subprocess
import sys

import pytest
from requests.exceptions import ConnectionError
from requests.exceptions import ReadTimeout

from bravado.exception import BravadoConnectionError
from bravado.exception import BravadoTimeoutError
from bravado.http_future import FutureAdapter


@pytest.mark.parametrize('protocol', range(pickle.HIGHEST_PROTOCOL + 1))
@pytest.mark.parametrize('original_type, method, base_type', [
    (ReadTimeout, '_raise_timeout_error', BravadoTimeoutError),
    (ConnectionError, '_raise_connection_error', BravadoConnectionError),
])
def test_adapter_error_pickle_round_trip(protocol, original_type, method, base_type):
    original = original_type('request failed')
    original.request_id = 'worker-1'
    with pytest.raises(base_type) as excinfo:
        getattr(FutureAdapter(), method)(original)
    error = excinfo.value
    error.retry_count = 2

    restored = pickle.loads(pickle.dumps(error, protocol=protocol))

    assert isinstance(restored, original_type)
    assert isinstance(restored, base_type)
    assert type(restored).__name__ == type(error).__name__
    assert restored.request_id == 'worker-1'
    assert restored.retry_count == 2
    assert restored.args == error.args


def test_adapter_timeout_unpickles_in_another_process():
    with pytest.raises(BravadoTimeoutError) as excinfo:
        FutureAdapter()._raise_timeout_error(ReadTimeout('request failed'))
    payload = pickle.dumps(excinfo.value)
    script = """
import pickle
import sys
from requests.exceptions import ReadTimeout
from bravado.exception import BravadoTimeoutError
error = pickle.load(sys.stdin.buffer)
assert isinstance(error, ReadTimeout)
assert isinstance(error, BravadoTimeoutError)
"""
    result = subprocess.run(
        [sys.executable, '-c', script], input=payload,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=30,
    )
    assert result.returncode == 0, result.stderr.decode()


class CustomTimeout(Exception):
    def __init__(self, *, request_id):
        self.request_id = request_id


def test_pickle_does_not_call_transport_constructor():
    with pytest.raises(BravadoTimeoutError) as excinfo:
        FutureAdapter()._raise_timeout_error(CustomTimeout(request_id='worker-2'))
    restored = pickle.loads(pickle.dumps(excinfo.value))
    assert isinstance(restored, CustomTimeout)
    assert isinstance(restored, BravadoTimeoutError)
    assert restored.request_id == 'worker-2'
