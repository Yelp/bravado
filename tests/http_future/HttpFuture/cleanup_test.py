# -*- coding: utf-8 -*-
import mock

from bravado.http_future import HttpFuture


def test_cleanup_on_gc(mock_future_adapter):
    http_future = HttpFuture(future=mock_future_adapter, response_adapter=mock.Mock())  # type: HttpFuture[None]
    del http_future
    assert mock_future_adapter.cleanup.call_count == 1
