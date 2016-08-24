# -*- coding: utf-8 -*-
from mock import Mock
import pytest

import crochet

from bravado.fido_client import FidoFutureAdapter


def test_eventual_result_not_cancelled():
    mock_eventual_result = Mock()
    adapter = FidoFutureAdapter(mock_eventual_result)

    adapter.result()
    assert mock_eventual_result.cancel.called is False


def test_eventual_result_cancelled_on_exception():
    mock_eventual_result = Mock(wait=Mock(side_effect=crochet.TimeoutError()))
    adapter = FidoFutureAdapter(mock_eventual_result)

    with pytest.raises(crochet.TimeoutError):
        adapter.result()

    assert mock_eventual_result.cancel.called is True
