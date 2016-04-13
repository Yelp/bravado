import mock
from mock import patch, Mock

import pytest
import six


try:
    from bravado.fido_client import FidoClient
except ImportError:
    FidoClient = Mock()


@pytest.mark.skipif(six.PY3, reason="twisted doesnt support py3 yet")
def test_request_no_timeouts_passed_to_fido():
    with patch('bravado.fido_client.fido.fetch') as fetch:
        request_params = dict(url='http://foo.com/')
        FidoClient().request(request_params)
        assert fetch.call_args == mock.call(
            url='http://foo.com/',
            body=None,
            headers={},
            method='GET',
        )


@pytest.mark.skipif(six.PY3, reason="twisted doesnt support py3 yet")
def test_request_timeout_passed_to_fido():
    with patch('bravado.fido_client.fido.fetch') as fetch:
        request_params = dict(url='http://foo.com/', timeout=1)
        FidoClient().request(request_params)
        assert fetch.call_args == mock.call(
            url='http://foo.com/',
            body=None,
            headers={},
            method='GET',
            timeout=1,
        )


@pytest.mark.skipif(six.PY3, reason="twisted doesnt support py3 yet")
def test_request_connect_timeout_passed_to_fido():
    with patch('bravado.fido_client.fido.fetch') as fetch:
        request_params = dict(url='http://foo.com/', connect_timeout=1)
        FidoClient().request(request_params)
        assert fetch.call_args == mock.call(
            url='http://foo.com/',
            body=None,
            headers={},
            method='GET',
            connect_timeout=1,
        )


@pytest.mark.skipif(six.PY3, reason="twisted doesnt support py3 yet")
def test_request_connect_timeout_and_timeout_passed_to_fido():
    with patch('bravado.fido_client.fido.fetch') as fetch:
        request_params = dict(url='http://foo.com/', connect_timeout=1,
                              timeout=2)
        FidoClient().request(request_params)
        assert fetch.call_args == mock.call(
            url='http://foo.com/',
            body=None,
            headers={},
            method='GET',
            connect_timeout=1,
            timeout=2,
        )
