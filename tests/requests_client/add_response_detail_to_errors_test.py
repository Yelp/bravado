from mock import Mock
import requests

import pytest

from bravado.exception import HTTPError
from bravado.requests_client import add_response_detail_to_errors


def test_response_message_gets_appended():
    e = requests.HTTPError('asdf')
    e.response = Mock(text='bla')

    with pytest.raises(HTTPError) as excinfo:
        add_response_detail_to_errors(e)
    assert 'asdf : bla' == str(excinfo.value)


def test_no_response_message_gets_appended():
    e = requests.HTTPError('asdf')

    with pytest.raises(HTTPError) as excinfo:
        add_response_detail_to_errors(e)
    assert 'asdf' == str(excinfo.value)
