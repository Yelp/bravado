# -*- coding: utf-8 -*-
import mock
import pytest

from bravado.config import BravadoConfig
from bravado.config import CONFIG_DEFAULTS
from bravado.config import get_response_metadata_class
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
    assert BravadoConfig.from_config_dict({}) == processed_default_config


def test_config_overrides_default_config(mock_log):
    config_dict = {
        'also_return_response': True,
        'disable_fallback_results': True,
        'response_metadata_class': 'tests.config_test.ResponseMetadata',
    }
    expected_config_dict = config_dict.copy()
    expected_config_dict['response_metadata_class'] = ResponseMetadata

    assert BravadoConfig.from_config_dict(config_dict)._asdict() == expected_config_dict
    assert mock_log.warning.call_count == 0


def test_ignore_unknown_configs(processed_default_config):
    config_dict = {'validate_swagger_spec': False}
    assert BravadoConfig.from_config_dict(config_dict) == processed_default_config


def test_get_response_metadata_class_invalid_str(mock_log):
    metadata_class = get_response_metadata_class('some_invalid_str')
    assert metadata_class is BravadoResponseMetadata
    assert mock_log.warning.call_count == 1
    assert 'Error while importing' in mock_log.warning.call_args[0][0]


def test_get_response_metadata_class_invalid_class(mock_log):
    metadata_class = get_response_metadata_class('tests.config_test.IncorrectResponseMetadata')
    assert metadata_class is BravadoResponseMetadata
    assert mock_log.warning.call_count == 1
    assert 'does not extend' in mock_log.warning.call_args[0][0]
