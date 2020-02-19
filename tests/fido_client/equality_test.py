# -*- coding: utf-8 -*-
import pytest

from bravado.fido_client import FidoClient
from bravado.fido_client import FidoFutureAdapter


@pytest.fixture
def http_client():
    return FidoClient()


def test_equality_of_the_same_http_client(http_client):
    assert http_client == http_client


def test_equality_of_different_http_clients_with_the_same_configurations(http_client):
    assert http_client == FidoClient()


def test_equality_of_different_http_clients_with_different_configurations(http_client):
    class CustomAdapter(FidoFutureAdapter):
        pass

    assert http_client != FidoClient(future_adapter_class=CustomAdapter)


def test_client_hashability(http_client):
    # The test wants to ensure that the HttpClient instance is hashable.
    # If calling hash does not throw an exception than we've validated the assumption
    hash(http_client)
