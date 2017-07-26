# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import mock

from bravado.fido_client import FidoResponseAdapter


def test_header_conversion():
    fido_response = mock.Mock(
        name='fido_response',
        headers={
            b'Content-Type': [b'application/json'],
            'x-weird-ä'.encode('latin1'): ['ümläüt'.encode('utf8')],
            b'X-Multiple': [b'donotuse', b'usethis'],
        },
    )

    response_adapter = FidoResponseAdapter(fido_response)
    assert response_adapter.headers == {
        'content-type': 'application/json',
        'X-WEIRD-ä': 'ümläüt',
        'X-Multiple': 'usethis',
    }
