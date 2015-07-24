from mock import patch, call, Mock
import pytest
import six


try:
    from bravado.fido_client import FidoClient
except ImportError:
    FidoClient = Mock()


@pytest.mark.skipif(six.PY3, reason="twisted doesnt support py3 yet")
def test_no_timeouts_passed_to_fido():
    with patch('bravado.fido_client.fido.fetch') as fetch:
        fido_client = FidoClient()
        request_params = dict(url='http://foo.com/')
        fido_client.request(request_params, response_callback=None)
        assert fetch.call_args == call(
            'http://foo.com/?', body='', headers={}, method='GET')


@pytest.mark.skipif(six.PY3, reason="twisted doesnt support py3 yet")
def test_timeout_passed_to_fido():
    with patch('bravado.fido_client.fido.fetch') as fetch:
        fido_client = FidoClient()
        request_params = dict(url='http://foo.com/', timeout=1)
        fido_client.request(request_params, response_callback=None)
        assert fetch.call_args == call(
            'http://foo.com/?', body='', headers={}, method='GET', timeout=1)


@pytest.mark.skipif(six.PY3, reason="twisted doesnt support py3 yet")
def test_connect_timeout_passed_to_fido():
    with patch('bravado.fido_client.fido.fetch') as fetch:
        fido_client = FidoClient()
        request_params = dict(url='http://foo.com/', connect_timeout=1)
        fido_client.request(request_params, response_callback=None)
        assert fetch.call_args == call(
            'http://foo.com/?', body='', headers={}, method='GET',
            connect_timeout=1)


@pytest.mark.skipif(six.PY3, reason="twisted doesnt support py3 yet")
def test_connect_timeout_and_timeout_passed_to_fido():
    with patch('bravado.fido_client.fido.fetch') as fetch:
        fido_client = FidoClient()
        request_params = dict(url='http://foo.com/', connect_timeout=1,
                              timeout=2)
        fido_client.request(request_params, response_callback=None)
        assert fetch.call_args == call(
            'http://foo.com/?', body='', headers={}, method='GET',
            connect_timeout=1, timeout=2)
