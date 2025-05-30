# -*- coding: utf-8 -*-
try:
    from unittest import mock
except ImportError:
    import mock
import pytest

from bravado.http_future import FutureAdapter


@pytest.fixture
def mock_future_adapter():
    return mock.Mock(
        spec=FutureAdapter,
        timeout_errors=None,
        connection_errors=None,
    )
