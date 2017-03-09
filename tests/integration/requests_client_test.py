# -*- coding: utf-8 -*-
from bravado.requests_client import RequestsClient
from tests.integration.conftest import ROUTE_1_RESPONSE
from tests.integration.conftest import ROUTE_2_RESPONSE


class TestServerRequestsClient:

    @classmethod
    def setup_class(cls):
        cls.http_client = RequestsClient()

    @classmethod
    def encode_expected_response(cls, response):
        if isinstance(response, bytes):
            return response.decode('utf-8')
        else:
            return str(response)

    def test_multiple_requests(self, threaded_http_server):

        request_one_params = {
            'method': 'GET',
            'headers': {},
            'url': "http://localhost:{0}/1".format(threaded_http_server),
            'params': {},
        }

        request_two_params = {
            'method': 'GET',
            'headers': {},
            'url': "http://localhost:{0}/2".format(threaded_http_server),
            'params': {},
        }

        http_future_1 = self.http_client.request(request_one_params)
        http_future_2 = self.http_client.request(request_two_params)
        resp_one = http_future_1.result(timeout=1)
        resp_two = http_future_2.result(timeout=1)

        assert resp_one.text == self.encode_expected_response(ROUTE_1_RESPONSE)
        assert resp_two.text == self.encode_expected_response(ROUTE_2_RESPONSE)

    def test_post_request(self, threaded_http_server):

        request_args = {
            'method': 'POST',
            'headers': {},
            'url': "http://localhost:{0}/double".format(threaded_http_server),
            'data': {"number": 3},
        }

        http_future = self.http_client.request(request_args)
        resp = http_future.result(timeout=1)

        assert resp.text == self.encode_expected_response(b'6')
