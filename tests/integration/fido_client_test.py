# -*- coding: utf-8 -*-
from bravado.fido_client import FidoClient
from tests.integration.requests_client_test import TestServerRequestsClient


class TestServerFidoClient(TestServerRequestsClient):

    @classmethod
    def setup_class(cls):
        cls.http_client = FidoClient()

    @classmethod
    def encode_expected_response(cls, response):
        return response
