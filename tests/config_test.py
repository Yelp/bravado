# -*- coding: utf-8 -*-
from bravado.config import BravadoConfig
from bravado.config import CONFIG_DEFAULTS


def test_default_value_for_every_config():
    assert set(CONFIG_DEFAULTS.keys()) == set(BravadoConfig._fields)


def test_empty_config_yields_default_config():
    assert BravadoConfig.from_config_dict({})._asdict() == CONFIG_DEFAULTS


def test_config_overrides_default_config():
    config_dict = {
        'also_return_response': True,
        'disable_fallback_results': True,
        'response_metadata_class': 'some.other.class',
    }

    assert BravadoConfig.from_config_dict(config_dict)._asdict() == config_dict


def test_ignore_unknown_configs():
    config_dict = {'validate_swagger_spec': False}
    assert BravadoConfig.from_config_dict(config_dict)._asdict() == CONFIG_DEFAULTS
