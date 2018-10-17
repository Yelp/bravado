# -*- coding: utf-8 -*-
from bravado.requests_client import RequestsFutureAdapter


def test_result_header_values_are_bytes(session, request):
    session.merge_environment_settings.return_value = {}
    request.headers = {b'X-Foo': b'hi'}
    RequestsFutureAdapter(session, request, misc_options={'ssl_verify': True, 'ssl_cert': None}).result()

    # prepare_request should be called with a request containing correctly
    # casted headers (bytestrings should be preserved)
    prepared_headers = session.prepare_request.call_args[0][0].headers
    assert prepared_headers == {b'X-Foo': b'hi'}
