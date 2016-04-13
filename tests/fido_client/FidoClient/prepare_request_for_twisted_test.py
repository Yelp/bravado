# -*- coding: utf-8 -*-
"""Unit tests for fido http client related methods
Not Tested:
1) Callbacks triggered by twisted and crochet
2) Timeouts by crochet's wait()
"""
from mock import Mock

import pytest
import six

try:
    from bravado.fido_client import FidoClient
except ImportError:
    FidoClient = Mock()  # Tests will be skipped in py3


@pytest.mark.skipif(
    six.PY3,
    reason="Fido client is not usable in py3 until twisted supports it",
)
def test_prepare_request_for_twisted():
    request_params = dict(
        url='http://example.com/api-docs',
        method='POST',
        data=42,
        params={'username': 'yelp'},
    )
    request_for_twisted = FidoClient.prepare_request_for_twisted(request_params)

    assert request_for_twisted == {
        'body': 42,
        'headers': {'Content-Type': 'application/x-www-form-urlencoded'},
        'method': 'POST',
        'url': 'http://example.com/api-docs?username=yelp'
    }


@pytest.mark.skipif(
    six.PY3,
    reason="Fido client is not usable in py3 until twisted supports it",
)
def test_prepare_request_for_twisted_timeouts_added():
    request_params = dict(
        url='http://example.com/api-docs', timeout=15, connect_timeout=15)
    request_for_twisted = FidoClient.prepare_request_for_twisted(request_params)

    assert request_for_twisted == {
        'body': None,
        'headers': {},
        'method': 'GET',
        'url': 'http://example.com/api-docs',
        'timeout': 15,
        'connect_timeout': 15,
    }
