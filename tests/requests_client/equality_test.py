# -*- coding: utf-8 -*-
import pytest

from bravado.requests_client import RequestsClient
from bravado.requests_client import RequestsFutureAdapter


@pytest.fixture
def http_client():
    return RequestsClient()


def test_equality_of_the_same_http_client(http_client):
    assert http_client == http_client


def test_equality_of_different_http_clients_with_the_same_configurations(http_client):
    assert http_client == RequestsClient()


def test_equality_of_different_http_clients_with_different_configurations(http_client):
    class CustomAdapter(RequestsFutureAdapter):
        pass

    assert http_client != RequestsClient(future_adapter_class=CustomAdapter)


def test_client_hashability(http_client):
    # The test wants to ensure that the HttpClient instance is hashable.
    # If calling hash does not throw an exception than we've validated the assumption
    hash(http_client)
