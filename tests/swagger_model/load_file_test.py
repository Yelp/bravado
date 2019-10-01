import pytest

from bravado.swagger_model import load_file

@pytest.mark.skip("Yelp/bravado 's testcases itself are failing")
def test_success():
    spec_json = load_file('test-data/2.0/simple/swagger.json')
    assert '2.0' == spec_json['swagger']


@pytest.mark.skip("Yelp/bravado 's testcases itself are failing")
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


@pytest.mark.skip("Yelp/bravado 's testcases itself are failing")
def test_spec_internal_representation_identical():
    spec_json = load_file('test-data/2.0/petstore/swagger.json')
    spec_yaml = load_file('test-data/2.0/petstore/swagger.yaml')

    assert spec_yaml == spec_json


@pytest.mark.skip("Yelp/bravado 's testcases itself are failing")
def test_non_existent_file():
    with pytest.raises(IOError) as excinfo:
        load_file('test-data/2.0/i_dont_exist.json')
    assert 'No such file or directory' in str(excinfo.value)
