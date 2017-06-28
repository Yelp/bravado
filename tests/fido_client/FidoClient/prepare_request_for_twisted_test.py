# -*- coding: utf-8 -*-
"""Unit tests for fido http client related methods
Not Tested:
1) Callbacks triggered by twisted and crochet
2) Timeouts by crochet's wait()
"""
from bravado.fido_client import FidoClient


def test_prepare_request_for_twisted_get():
    request_params = {
        'url': 'http://example.com/api-docs'
    }
    request_for_twisted = FidoClient.prepare_request_for_twisted(request_params)

    assert request_for_twisted == {
        'body': None,
        'headers': {},
        'method': 'GET',
        'url': 'http://example.com/api-docs',
    }


def test_prepare_request_for_twisted_body_is_bytes():
    request_params = {
        'url': 'http://example.com/api-docs',
        'method': 'POST',
        'data': 42,
        'params': {'username': 'yelp'},
    }
    request_for_twisted = FidoClient.prepare_request_for_twisted(request_params)

    assert request_for_twisted == {
        'body': b'42',
        'headers': {'Content-Type': 'application/x-www-form-urlencoded'},
        'method': 'POST',
        'url': 'http://example.com/api-docs?username=yelp'
    }


def test_prepare_request_for_twisted_header_values_are_bytes():
    request_params = {
        'url': 'http://example.com/api-docs',
        'headers': {b'X-Foo': b'hi'},
        'method': 'GET',
    }
    request_for_twisted = FidoClient.prepare_request_for_twisted(request_params)

    assert request_for_twisted == {
        'body': None,
        'headers': {'X-Foo': b'hi'},
        'method': 'GET',
        'url': 'http://example.com/api-docs'
    }


def test_prepare_request_for_twisted_timeouts_added():
    request_params = {
        'url': 'http://example.com/api-docs',
        'timeout': 15,
        'connect_timeout': 15
    }
    request_for_twisted = FidoClient.prepare_request_for_twisted(request_params)

    assert request_for_twisted == {
        'body': None,
        'headers': {},
        'method': 'GET',
        'url': 'http://example.com/api-docs',
        'timeout': 15,
        'connect_timeout': 15,
    }
