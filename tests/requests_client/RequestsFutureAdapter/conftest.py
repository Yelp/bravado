# -*- coding: utf-8 -*-
import pytest
from mock import Mock
from requests.sessions import Session


@pytest.fixture
def request_mock():
    return Mock(url='http://foo.com')


@pytest.fixture
def session_mock():
    return Mock(spec=Session)
