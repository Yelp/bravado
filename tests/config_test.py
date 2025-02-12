# -*- coding: utf-8 -*-
import mock
import pytest

from bravado.config import _get_response_metadata_class
from bravado.config import bravado_config_from_config_dict
from bravado.config import BravadoConfig
from bravado.config import CONFIG_DEFAULTS
from bravado.config import RequestConfig
from bravado.response import BravadoResponseMetadata


class IncorrectResponseMetadata(object):
    pass


class ResponseMetadata(BravadoResponseMetadata):
    pass


@pytest.fixture
def mock_log():
    with mock.patch('bravado.config.log') as mock_log:
        yield mock_log


def test_default_value_for_every_config():
    assert set(CONFIG_DEFAULTS.keys()) == set(BravadoConfig._fields)


def test_empty_config_yields_default_config(processed_default_config):
    assert bravado_config_from_config_dict({}) == processed_default_config


def test_config_overrides_default_config(mock_log):
    config_dict = {
        'also_return_response': True,
        'disable_fallback_results': True,
        'response_metadata_class': 'tests.config_test.ResponseMetadata',
        'sensitive_headers': ['Authorization'],
    }
    expected_config_dict = config_dict.copy()
    expected_config_dict['response_metadata_class'] = ResponseMetadata

    assert bravado_config_from_config_dict(config_dict)._asdict() == expected_config_dict
    assert mock_log.warning.call_count == 0


def test_ignore_unknown_configs(processed_default_config):
    config_dict = {'validate_swagger_spec': False}
    assert bravado_config_from_config_dict(config_dict) == processed_default_config


def test_get_response_metadata_class_invalid_str(mock_log):
    metadata_class = _get_response_metadata_class('some_invalid_str')
    assert metadata_class is BravadoResponseMetadata
    assert mock_log.warning.call_count == 1
    assert 'Error while importing' in mock_log.warning.call_args[0][0]


def test_get_response_metadata_class_invalid_class(mock_log):
    metadata_class = _get_response_metadata_class('tests.config_test.IncorrectResponseMetadata')
    assert metadata_class is BravadoResponseMetadata
    assert mock_log.warning.call_count == 1
    assert 'does not extend' in mock_log.warning.call_args[0][0]


def test_empty_request_config():
    request_config = RequestConfig({}, also_return_response_default=False)
    _assert_request_config_equals(
        request_config,
        also_return_response=False,
        force_fallback_result=False,
        response_callbacks=[],
        connect_timeout=None,
        headers={},
        use_msgpack=False,
        timeout=None,
        additional_properties={},
    )


def test_request_config_all_values():
    request_options = {
        'also_return_response': True,
        'force_fallback_result': True,
        'response_callbacks': [lambda ir, op: None],
        'connect_timeout': 0.2,
        'headers': {'X-Speed-Up': '1'},
        'use_msgpack': True,
        'timeout': 2,
        'http_client_option': 'a value',
    }

    request_config = RequestConfig(request_options, also_return_response_default=False)
    request_options['additional_properties'] = {
        'http_client_option': request_options.pop('http_client_option')
    }
    _assert_request_config_equals(request_config, **request_options)


def _assert_request_config_equals(request_config, **kwargs):
    for name, value in kwargs.items():
        assert hasattr(request_config, name)
        assert getattr(request_config, name) == value
