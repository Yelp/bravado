# -*- coding: utf-8 -*-
"""Unit tests for fido http client related methods
Not Tested:
1) Callbacks triggered by twisted and crochet
2) Timeouts by crochet's wait()
"""
from mock import patch, Mock

import pytest
import six

try:
    from bravado.fido_client import FidoClient
except ImportError:
    FidoClient = Mock()  # Tests will be skipped in py3

from bravado.http_client import APP_FORM
import bravado.exception


@pytest.mark.skipif(
    six.PY3,
    reason="Fido client is not usable in py3 until twisted supports it",
)
def test_stringify_fido_body_returns_file_producer():
    def_str = 'bravado.fido_client.param_stringify_body'
    with patch(def_str) as mock_stringify:
        mock_stringify.return_value = '42'
        body = {'data': 42, 'headers': {}}
        resp = bravado.fido_client.stringify_body(body)

        assert '42' == resp

        mock_stringify.assert_called_once_with(body['data'])


@pytest.mark.skipif(
    six.PY3,
    reason="Fido client is not usable in py3 until twisted supports it",
)
def test_stringify_files_creates_correct_body_content():
    fake_file = Mock()
    fake_file.read.return_value = "contents"
    request = {'files': {'fake': fake_file},
               'headers': {'content-type': 'tmp'}}
    with patch('bravado.multipart_response.get_random_boundary',
               return_value='zz'):
        resp = bravado.fido_client.stringify_body(request)

        expected_contents = (
            '--zz\r\nContent-Disposition: form-data; name=fake;' +
            ' filename=fake\r\n\r\ncontents\r\n--zz--\r\n')
        assert 'multipart/form-data; boundary=zz' == \
               request['headers']['content-type']
        assert expected_contents == resp


@pytest.mark.skipif(
    six.PY3,
    reason="Fido client is not usable in py3 until twisted supports it",
)
def test_stringify_files_creates_correct_form_content():
    request = {'data': {'id': 42, 'name': 'test'},
               'headers': {'content-type': APP_FORM}}
    resp = bravado.fido_client.stringify_body(request)

    assert six.moves.urllib.parse.parse_qs('id=42&name=test') == \
        six.moves.urllib.parse.parse_qs(resp)


@pytest.mark.skipif(
    six.PY3,
    reason="Fido client is not usable in py3 until twisted supports it",
)
def test_start_request_with_only_url():
    url = 'http://example.com/api-docs'
    fido_client = bravado.fido_client.FidoClient()
    # ugly mock, but this method runs in a twisted reactor which is
    # difficult to mock
    fido_client.fetch_deferred = Mock()

    with patch('fido.fetch') as mock_fetch:
        fido_client.request(dict(url=url))

    mock_fetch.assert_called_once_with(
        '{0}?'.format(url), body='', headers={}, method='GET')
