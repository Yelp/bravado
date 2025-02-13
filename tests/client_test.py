# -*- coding: utf-8 -*-
import typing
from copy import deepcopy

import mock
import pytest

from bravado.client import CallableOperation
from bravado.client import SwaggerClient
from bravado.config import CONFIG_DEFAULTS
from bravado.http_client import HttpClient
from bravado.requests_client import RequestsClient
from bravado.swagger_model import load_file


_HTTP_CLIENTS = [None, RequestsClient()]  # type: typing.List[typing.Optional[HttpClient]]
try:
    from bravado.fido_client import FidoClient
    _HTTP_CLIENTS.append(FidoClient())
except ImportError:
    pass


@pytest.fixture
def mock_spec():
    with mock.patch('bravado.client.Spec') as _mock:
        yield _mock


def test_remove_bravado_configs(mock_spec, processed_default_config):
    config = CONFIG_DEFAULTS.copy()
    config['validate_swagger_spec'] = False  # bravado_core config

    SwaggerClient.from_spec({}, config=config)

    mock_spec.from_dict.assert_called_once_with(
        {},  # spec_dict
        None,  # spec_url
        mock.ANY,  # http_client
        {
            'bravado': processed_default_config,
            'validate_swagger_spec': False,
        },  # config
    )


def test_also_return_response(mock_spec):
    with mock.patch('bravado.client.SwaggerClient.__init__') as mock_init:
        mock_init.return_value = None
        SwaggerClient.from_spec({}, config={'also_return_response': True})

    mock_init.assert_called_once_with(
        mock_spec.from_dict.return_value,
        also_return_response=True,
    )


@pytest.fixture(
    params=_HTTP_CLIENTS,
    ids=[type(http_client).__name__ for http_client in _HTTP_CLIENTS],
)
def swagger_client(request):
    return SwaggerClient.from_spec(
        spec_dict=load_file('test-data/2.0/simple/swagger.json'),
        http_client=request.param,
    )


def test_swagger_client_id_deep_copiable(swagger_client):
    """
    The goal of the test is to ensure that the SwaggerClient is deepcopiable
    The test should be considered successful if calling deepcopy on a
    SwaggerClient instance does not raise exceptions.
    """
    swagger_client_copy = deepcopy(swagger_client)

    assert swagger_client.is_equal(swagger_client_copy)
    assert id(swagger_client) != id(swagger_client_copy)
    # NOTE: client.__also_return_response is not tested because its type is immutable (bool),
    #       so deepcopy would return the same instance
    assert id(swagger_client.swagger_spec) != id(swagger_client_copy.swagger_spec)


def test_equality_of_the_same_swagger_client(swagger_client):
    assert swagger_client.is_equal(swagger_client)


def test_equality_of_different_swagger_clients(swagger_client):
    assert not swagger_client.is_equal(
        SwaggerClient.from_spec(spec_dict=load_file('test-data/2.0/petstore/swagger.json')),
    )


def test_swagger_client_hashability(swagger_client):
    # The test wants to ensure that the SwaggertClient instance is hashable.
    # If calling hash does not throw an exception than we've validated the assumption
    hash(swagger_client)


def test_sanitize_kwargs_for_logging(mock_spec):
    mock_operation = mock.MagicMock()
    mock_operation.swagger_spec.config = CONFIG_DEFAULTS.copy()
    operation = CallableOperation(mock_operation)
    mock_args = {
        'foo': 'bar',
        '_request_options': {
            'headers': {
                'User-Agent': 'something',
                'Authorization': 'verysecret',
            },
        },
    }
    assert operation._sanitize_kwargs_for_logging(mock_args) == {
        'foo': 'bar',
        '_request_options': {
            'headers': {
                'User-Agent': 'something',
                'Authorization': '*redacted*',
            },
        },
    }
    # checking original args dict did not get modified
    assert mock_args == {
        'foo': 'bar',
        '_request_options': {
            'headers': {
                'User-Agent': 'something',
                'Authorization': 'verysecret',
            },
        },
    }


def test_sanitize_kwargs_for_logging_multiple(mock_spec):
    mock_operation = mock.MagicMock()
    mock_operation.swagger_spec.config = CONFIG_DEFAULTS.copy()
    mock_operation.swagger_spec.config['sensitive_headers'] = ['Authorization', 'X-Whatever-Auth']
    operation = CallableOperation(mock_operation)
    mock_args = {
        'foo': 'bar',
        '_request_options': {
            'headers': {
                'User-Agent': 'something',
                'Authorization': 'verysecret',
                'X-Whatever-Auth': 'alsosecret',
            },
        },
    }
    assert operation._sanitize_kwargs_for_logging(mock_args) == {
        'foo': 'bar',
        '_request_options': {
            'headers': {
                'User-Agent': 'something',
                'Authorization': '*redacted*',
                'X-Whatever-Auth': '*redacted*',
            },
        },
    }
    # checking original args dict did not get modified
    assert mock_args == {
        'foo': 'bar',
        '_request_options': {
            'headers': {
                'User-Agent': 'something',
                'Authorization': 'verysecret',
                'X-Whatever-Auth': 'alsosecret',
            },
        },
    }
