# -*- coding: utf-8 -*-
import pytest
import requests
from mock import mock

from bravado.exception import BravadoTimeoutError
from bravado.requests_client import RequestsClient
from bravado.requests_client import RequestsFutureAdapter
from bravado.swagger_model import Loader
from tests.integration.conftest import ROUTE_1_RESPONSE
from tests.integration.conftest import ROUTE_2_RESPONSE


class TestServerRequestsClient:

    http_client_type = RequestsClient
    http_future_adapter_type = RequestsFutureAdapter

    @classmethod
    def setup_class(cls):
        if cls.http_client_type is None:
            raise RuntimeError('Define http_client_type for {}'.format(cls.__name__))
        if cls.http_future_adapter_type is None:
            raise RuntimeError('Define http_future_adapter_type for {}'.format(cls.__name__))
        cls.http_client = cls.http_client_type()

    @classmethod
    def encode_expected_response(cls, response):
        if isinstance(response, bytes):
            return response.decode('utf-8')
        else:
            return str(response)

    def test_fetch_specs(self, threaded_http_server, petstore_dict):
        loader = Loader(
            http_client=self.http_client,
            request_headers={'boolean-header': True},
        )
        spec = loader.load_spec('{server_address}/swagger.json'.format(server_address=threaded_http_server))
        assert spec == petstore_dict

    def test_multiple_requests(self, threaded_http_server):

        request_one_params = {
            'method': 'GET',
            'headers': {},
            'url': '{server_address}/1'.format(server_address=threaded_http_server),
            'params': {},
        }

        request_two_params = {
            'method': 'GET',
            'headers': {},
            'url': '{server_address}/2'.format(server_address=threaded_http_server),
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
            'url': '{server_address}/double'.format(server_address=threaded_http_server),
            'data': {"number": 3},
        }

        http_future = self.http_client.request(request_args)
        resp = http_future.result(timeout=1)

        assert resp.text == self.encode_expected_response(b'6')

    def test_boolean_header(self, threaded_http_server):
        response = self.http_client.request({
            'method': 'GET',
            'headers': {'boolean-header': True},
            'url': '{server_address}/1'.format(server_address=threaded_http_server),
            'params': {},
        }).result(timeout=1)

        assert response.text == self.encode_expected_response(ROUTE_1_RESPONSE)

    def test_timeout_errors_are_thrown_as_BravadoTimeoutError(self, threaded_http_server):
        timeout_errors = getattr(self.http_future_adapter_type, 'timeout_errors', [])
        if not timeout_errors:
            pytest.skip('{} does NOT defines timeout_errors'.format(self.http_future_adapter_type))

        with pytest.raises(BravadoTimeoutError):
            self.http_client.request({
                'method': 'GET',
                'url': '{server_address}/sleep?sec=0.1'.format(server_address=threaded_http_server),
                'params': {},
            }).result(timeout=0.01)

    def test_timeout_errors_are_catchable_with_original_exception_types(self, threaded_http_server):
        timeout_errors = getattr(self.http_future_adapter_type, 'timeout_errors', [])
        if not timeout_errors:
            pytest.skip('{} does NOT defines timeout_errors'.format(self.http_future_adapter_type))

        for expected_exception in timeout_errors:
            with pytest.raises(expected_exception):
                self.http_client.request({
                    'method': 'GET',
                    'url': '{server_address}/sleep?sec=0.1'.format(server_address=threaded_http_server),
                    'params': {},
                }).result(timeout=0.01)


class FakeRequestsFutureAdapter(RequestsFutureAdapter):
    timeout_errors = []


class FakeRequestsClient(RequestsClient):
    @mock.patch('bravado.requests_client.RequestsFutureAdapter', FakeRequestsFutureAdapter)
    def request(self, *args, **kwargs):
        return super(FakeRequestsClient, self).request(*args, **kwargs)


class TestServerRequestsClientFake(TestServerRequestsClient):
    """
    This test class uses as http client a requests client that has no timeout error specified.
    This is needed to ensure that the changes are back compatible
    """

    http_client_type = FakeRequestsClient
    http_future_adapter_type = FakeRequestsFutureAdapter

    def test_timeout_error_not_throws_BravadoTimeoutError_if_no_timeout_errors_specified(self, threaded_http_server):
        try:
            self.http_client.request({
                'method': 'GET',
                'url': '{server_address}/sleep?sec=0.1'.format(server_address=threaded_http_server),
                'params': {},
            }).result(timeout=0.01)
        except BravadoTimeoutError:
            pytest.fail('DID RAISE BravadoTimeoutError')
        except Exception:
            pass

    def test_timeout_errors_are_catchable_with_original_exception_types(self, threaded_http_server):
        with pytest.raises(requests.Timeout):
            self.http_client.request({
                'method': 'GET',
                'url': '{server_address}/sleep?sec=0.1'.format(server_address=threaded_http_server),
                'params': {},
            }).result(timeout=0.01)
