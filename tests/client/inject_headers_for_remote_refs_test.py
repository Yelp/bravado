# -*- coding: utf-8 -*-
from bravado_core.operation import Operation
try:
    from unittest.mock import Mock
except ImportError:
    from mock import Mock

from bravado.client import inject_headers_for_remote_refs


def test_headers_inject_when_retrieving_remote_ref():
    callable = Mock()
    headers = {'X-Foo': 'bar'}
    injected_callable = inject_headers_for_remote_refs(callable, headers)
    request_params = {
        'method': 'GET',
        'url': 'http://foo.bar.com/paths.json'
    }
    injected_callable(request_params)
    assert 'headers' in request_params


def test_headers_not_injected_when_making_a_service_call():
    callable = Mock()
    headers = {'X-Foo': 'bar'}
    injected_callable = inject_headers_for_remote_refs(callable, headers)
    request_params = {
        'method': 'GET',
        'url': 'http://foo.bar.com/users/1'
    }
    injected_callable(request_params, operation=Mock(spec=Operation))
    assert 'headers' not in request_params
