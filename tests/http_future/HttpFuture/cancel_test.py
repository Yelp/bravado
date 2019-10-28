# -*- coding: utf-8 -*-
import mock
import pytest
from bravado_core.response import IncomingResponse

from bravado.http_future import FutureAdapter
from bravado.http_future import HttpFuture


@pytest.fixture
def mock_log():
    with mock.patch('bravado.http_future.log') as mock_log:
        yield mock_log


class MyFutureAdapter(FutureAdapter):
    pass


def test_cancel():
    mock_future_adapter = mock.Mock()
    future = HttpFuture(
        future=mock_future_adapter,
        response_adapter=lambda x: IncomingResponse(),
    )  # type: HttpFuture[None]
    future.cancel()

    assert mock_future_adapter.cancel.call_count == 1


def test_cancel_is_backwards_compatible(mock_log):
    future_adapter = MyFutureAdapter()
    future = HttpFuture(
        future=future_adapter,
        response_adapter=lambda x: IncomingResponse(),
    )  # type: HttpFuture[None]
    future.cancel()

    assert mock_log.warning.call_count == 1
