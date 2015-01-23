import pytest

from bravado.swagger_model import load_file


def test_success():
    spec_json = load_file('test-data/2.0/simple/swagger.json')
    assert '2.0' == spec_json['swagger']


def test_non_existant_file():
    with pytest.raises(IOError) as excinfo:
        load_file('test-data/2.0/i_dont_exist.json')
    assert 'No such file or directory' in str(excinfo.value)
