# -*- coding: utf-8 -*-
import pytest
from mock import Mock
from requests.sessions import Session


@pytest.fixture
def request():
    return Mock(url='http://foo.com')


@pytest.fixture
def session():
    return Mock(spec=Session)
