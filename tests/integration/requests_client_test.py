# -*- coding: utf-8 -*-
import json

import mock
import pytest
import requests
import requests.exceptions
from msgpack import packb, unpackb
from bravado_core.content_type import APP_MSGPACK

from bravado.client import SwaggerClient
from bravado.exception import BravadoTimeoutError
from bravado.requests_client import RequestsClient
from bravado.requests_client import RequestsFutureAdapter
from bravado.swagger_model import Loader
from tests.integration.conftest import API_RESPONSE
from tests.integration.conftest import ROUTE_1_RESPONSE
from tests.integration.conftest import ROUTE_2_RESPONSE
from tests.integration.conftest import SWAGGER_SPEC_DICT


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

    def test_fetch_specs(self, threaded_http_server):
        loader = Loader(
            http_client=self.http_client,
            request_headers={'boolean-header': True},
        )
        spec = loader.load_spec('{server_address}/swagger.json'.format(server_address=threaded_http_server))
        assert spec == SWAGGER_SPEC_DICT

    @pytest.fixture
    def swagger_client(self, threaded_http_server):
        return SwaggerClient.from_url(
            spec_url='{server_address}/swagger.json'.format(
                server_address=threaded_http_server),
            http_client=self.http_client,
            config={'use_models': False, 'also_return_response': True}
        )

    def test_swagger_client_json_response(self, swagger_client):
        marshaled_response, raw_response = swagger_client.json.get_json().result(timeout=1)
        assert marshaled_response == API_RESPONSE
        assert raw_response.raw_bytes == json.dumps(API_RESPONSE).encode('utf-8')

    def test_swagger_client_msgpack_response_without_flag(self, swagger_client):
        marshaled_response, raw_response = swagger_client.json_or_msgpack.get_json_or_msgpack().result(timeout=1)
        assert marshaled_response == API_RESPONSE
        assert raw_response.raw_bytes == json.dumps(API_RESPONSE).encode('utf-8')

    def test_swagger_client_msgpack_response_with_flag(self, swagger_client):
        marshaled_response, raw_response = swagger_client.json_or_msgpack.get_json_or_msgpack(
            _request_options={
                'use_msgpack': True,
            },
        ).result(timeout=1)
        assert marshaled_response == API_RESPONSE
        assert raw_response.raw_bytes == packb(API_RESPONSE)

    def test_swagger_client_special_chars_query(self, swagger_client):
        message = 'My Me$$age with %pecial characters?"'
        marshaled_response, _ = swagger_client.echo.get_echo(message=message).result(timeout=1)
        assert marshaled_response == {'message': message}

    def test_swagger_client_special_chars_path(self, swagger_client):
        marshaled_response, _ = swagger_client.char_test.get_char_test(special='spe%ial?').result(timeout=1)
        assert marshaled_response == API_RESPONSE

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

    def test_msgpack_support(self, threaded_http_server):
        response = self.http_client.request({
            'method': 'GET',
            'url': '{server_address}/json_or_msgpack'.format(server_address=threaded_http_server),
            'params': {},
            'headers': {
                'Accept': APP_MSGPACK,
            },
        }).result(timeout=1)

        assert response.headers['Content-Type'] == APP_MSGPACK
        assert unpackb(response.raw_bytes, encoding='utf-8') == API_RESPONSE

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

    def test_timeout_errors_are_catchable_as_requests_timeout(self, threaded_http_server):
        if not self.http_client_type == RequestsClient:
            pytest.skip('{} is not using RequestsClient'.format(self.http_future_adapter_type))

        with pytest.raises(requests.exceptions.Timeout):
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
