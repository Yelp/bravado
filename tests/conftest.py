# -*- coding: utf-8 -*-
import json
import os

import pytest


@pytest.fixture
def test_dir():
    return os.path.abspath(os.path.dirname(__file__))


@pytest.fixture
def petstore_dict(test_dir):
    fpath = os.path.join(test_dir, '../test-data/2.0/petstore/swagger.json')
    with open(fpath) as f:
        return json.load(f)
