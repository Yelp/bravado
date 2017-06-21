# -*- coding: utf-8 -*-
import crochet
import fido.exceptions
import pytest
from mock import Mock

from bravado.fido_client import FidoFutureAdapter


def test_eventual_result_not_cancelled():
    mock_eventual_result = Mock()
    adapter = FidoFutureAdapter(mock_eventual_result)

    adapter.result()
    assert mock_eventual_result.cancel.called is False


def test_eventual_result_cancelled_on_exception():
    mock_eventual_result = Mock(wait=Mock(side_effect=crochet.TimeoutError()))
    adapter = FidoFutureAdapter(mock_eventual_result)

    with pytest.raises(fido.exceptions.HTTPTimeoutError) as exc_info:
        adapter.result(timeout=1)

    assert mock_eventual_result.cancel.called is True
    assert str(exc_info.value).startswith('Connection was closed by fido after blocking for timeout=1 seconds')
