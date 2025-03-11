# -*- coding: utf-8 -*-
import pytest
try:
    from unittest.mock import Mock
except ImportError:
    from mock import Mock
from requests.sessions import Session


@pytest.fixture
def request_mock():
    return Mock(url='http://foo.com')


@pytest.fixture
def session_mock():
    return Mock(spec=Session)
