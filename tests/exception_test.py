# -*- coding: utf-8 -*-
import pytest
from requests.models import Response

from bravado.exception import HTTPError
from bravado.requests_client import RequestsResponseAdapter


@pytest.fixture
def response_500():
    requests_response = Response()
    requests_response.status_code = 500
    requests_response.reason = "Server Error"
    return requests_response


def test_response_only(response_500):
    incoming_response = RequestsResponseAdapter(response_500)
    assert str(HTTPError(incoming_response)) == '500 Server Error'


def test_response_and_message(response_500):
    incoming_response = RequestsResponseAdapter(response_500)
    actual = str(HTTPError(incoming_response, message="Kaboom"))
    assert actual == '500 Server Error: Kaboom'


def test_response_and_swagger_result(response_500):
    incoming_response = RequestsResponseAdapter(response_500)
    actual = str(HTTPError(incoming_response, swagger_result={'msg': 'Kaboom'}))
    assert actual == "500 Server Error: {'msg': 'Kaboom'}"


def test_response_and_message_and_swagger_result(response_500):
    incoming_response = RequestsResponseAdapter(response_500)
    actual = str(HTTPError(
        incoming_response,
        message="Holy moly!",
        swagger_result={'msg': 'Kaboom'}))
    assert actual == "500 Server Error: Holy moly!: {'msg': 'Kaboom'}"
