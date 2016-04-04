# -*- coding: utf-8 -*-
"""Unit tests for fido http client related methods
Not Tested:
1) Callbacks triggered by twisted and crochet
2) Timeouts by crochet's wait()
"""
import mock
from mock import patch, Mock

import pytest
import six

try:
    from bravado.fido_client import FidoClient
except ImportError:
    FidoClient = Mock()  # Tests will be skipped in py3


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


@pytest.mark.skipif(
    six.PY3,
    reason="Fido client is not usable in py3 until twisted supports it",
)
def test_prepare_request_for_crochet():
    request_params = dict(
        url='http://example.com/api-docs',
        method='POST',
        data=42,
        params={'username': 'yelp'},
    )
    request_for_crochet = FidoClient.prepare_request_for_crochet(request_params)

    assert request_for_crochet == {
        'body': 42,
        'headers': {'Content-Type': 'application/x-www-form-urlencoded'},
        'method': 'POST',
        'url': 'http://example.com/api-docs?username=yelp'
    }


@pytest.mark.skipif(
    six.PY3,
    reason="Fido client is not usable in py3 until twisted supports it",
)
def test_prepare_request_for_crochet_timeouts_added():
    request_params = dict(
        url='http://example.com/api-docs', timeout=15, connect_timeout=15)
    request_for_crochet = FidoClient.prepare_request_for_crochet(request_params)

    assert request_for_crochet == {
        'body': None,
        'headers': {},
        'method': 'GET',
        'url': 'http://example.com/api-docs',
        'timeout': 15,
        'connect_timeout': 15,
    }
