# -*- coding: utf-8 -*-
import json
import os

import pytest

from bravado.config import BravadoConfig
from bravado.response import BravadoResponseMetadata


@pytest.fixture
def test_dir():
    return os.path.abspath(os.path.dirname(__file__))


@pytest.fixture
def processed_default_config(**kwargs):
    # test_config_overrides_default_config makes assumptions about the default config;
    # if you're changing a default, please change that test as well as this fixture too.
    config = {
        'also_return_response': False,
        'disable_fallback_results': False,
        'response_metadata_class': BravadoResponseMetadata,
    }
    config.update(**kwargs)
    return BravadoConfig(**config)  # type: ignore


@pytest.fixture
def petstore_dict(test_dir):
    fpath = os.path.join(test_dir, '../test-data/2.0/petstore/swagger.json')
    with open(fpath) as f:
        return json.load(f)
