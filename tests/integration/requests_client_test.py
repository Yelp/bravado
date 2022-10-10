# -*- coding: utf-8 -*-
import typing
import json

import pytest
import requests.exceptions

import bravado.testing.integration_test
from bravado.exception import BravadoTimeoutError
from bravado.requests_client import RequestsClient
from bravado.requests_client import RequestsFutureAdapter
from bravado.testing.integration_test import IntegrationTestsBaseClass


class TestServerRequestsClient(IntegrationTestsBaseClass):
    http_client_type = RequestsClient
    http_future_adapter_type = RequestsFutureAdapter
    connection_errors_exceptions = {
        requests.exceptions.ConnectionError(),
    }

    def test_timeout_errors_are_catchable_as_requests_timeout(
        self, swagger_http_server,
    ):
        with pytest.raises(requests.exceptions.Timeout):
            self.http_client.request({
                'method': 'GET',
                'url': '{server_address}/sleep?sec=0.1'.format(
                    server_address=swagger_http_server),
                'params': {},
            }).result(timeout=0.01)


class TestServerRequestsFollowRedirect(IntegrationTestsBaseClass):
    http_client_type = RequestsClient
    http_future_adapter_type = RequestsFutureAdapter
    connection_errors_exceptions = {
        requests.exceptions.ConnectionError(),
    }
    def test_swagger_client_follow_redirects(
            self, swagger_http_server, swagger_client, result_getter,
    ):
        swagger_client.swagger_spec.api_url = swagger_http_server
        marshaled_response, raw_response = result_getter(
            swagger_client.redirect.redirect_test(
                _request_options={
                    'follow_redirects': True,
                }
            ),
            timeout=0.1,
        )

        assert marshaled_response == bravado.testing.integration_test.API_RESPONSE
        assert raw_response.raw_bytes == json.dumps(bravado.testing.integration_test.API_RESPONSE).encode('utf-8')


class FakeRequestsFutureAdapter(RequestsFutureAdapter):
    timeout_errors = ()
    connection_errors = ()


class FakeRequestsClient(RequestsClient):
    def __init__(self, *args, **kwargs):
        kwargs['future_adapter_class'] = FakeRequestsFutureAdapter
        super(FakeRequestsClient, self).__init__(*args, **kwargs)


class TestServerRequestsClientFake(IntegrationTestsBaseClass):
    """
    This test class uses as http client a requests client that has no timeout error specified.
    This is needed to ensure that the changes are back compatible
    """

    http_client_type = FakeRequestsClient
    http_future_adapter_type = FakeRequestsFutureAdapter
    connection_errors_exceptions = set()  # type: typing.Set[Exception]

    def test_timeout_error_not_throws_BravadoTimeoutError_if_no_timeout_errors_specified(self, swagger_http_server):
        try:
            self.http_client.request({
                'method': 'GET',
                'url': '{server_address}/sleep?sec=0.1'.format(server_address=swagger_http_server),
                'params': {},
            }).result(timeout=0.01)
        except Exception as e:
            assert not isinstance(e, BravadoTimeoutError)
