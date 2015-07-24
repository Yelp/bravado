from mock import patch, call
from bravado.fido_client import FidoClient


@patch('bravado.fido_client.fido.fetch')
def test_timeout_passed_to_fido(fetch):
    fido_client = FidoClient()
    request_params = dict(url='http://foo.com/', timeout=1)
    fido_client.request(request_params, response_callback=None)
    assert fetch.call_args == call(
        'http://foo.com/?', body='', headers={}, method='GET', timeout=1)


@patch('bravado.fido_client.fido.fetch')
def test_connect_timeout_passed_to_fido(fetch):
    fido_client = FidoClient()
    request_params = dict(url='http://foo.com/', connect_timeout=1)
    fido_client.request(request_params, response_callback=None)
    assert fetch.call_args == call(
        'http://foo.com/?', body='', headers={}, method='GET',
        connect_timeout=1)


@patch('bravado.fido_client.fido.fetch')
def test_connect_timeout_and_timeout_passed_to_fido(fetch):
    fido_client = FidoClient()
    request_params = dict(url='http://foo.com/', connect_timeout=1, timeout=2)
    fido_client.request(request_params, response_callback=None)
    assert fetch.call_args == call(
        'http://foo.com/?', body='', headers={}, method='GET',
        connect_timeout=1, timeout=2)
