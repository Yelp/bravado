# -*- coding: utf-8 -*-
import os
import sys

import pytest

from bravado.swagger_model import load_file


def test_success():
    spec_json = load_file('test-data/2.0/simple/swagger.json')
    assert '2.0' == spec_json['swagger']


@pytest.mark.parametrize(
    'filename',
    (
        ('test-data/2.0/simple/swagger.yaml'),
        ('test-data/2.0/petstore/swagger.yaml'),
    ),
)
def test_success_yaml(filename):
    spec_yaml = load_file(filename)
    assert '2.0' == spec_yaml['swagger']


def test_spec_internal_representation_identical():
    spec_json = load_file('test-data/2.0/petstore/swagger.json')
    spec_yaml = load_file('test-data/2.0/petstore/swagger.yaml')

    assert spec_yaml == spec_json


def test_non_existent_file():
    with pytest.raises(IOError) as excinfo:
        load_file(os.path.join('test-data', '2.0', 'i_dont_exist.json'))
    if sys.platform == "win32":
        assert 'The system cannot find the file specified' in str(excinfo.value)
    else:
        assert 'No such file or directory' in str(excinfo.value)
