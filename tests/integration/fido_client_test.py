# -*- coding: utf-8 -*-
from bravado.fido_client import FidoClient
from bravado.fido_client import FidoFutureAdapter
from tests.integration import requests_client_test


class TestServerFidoClient(requests_client_test.TestServerRequestsClient):

    http_client_type = FidoClient
    http_future_adapter_type = FidoFutureAdapter

    @classmethod
    def encode_expected_response(cls, response):
        return response
