from bravado.mapping.exception import SwaggerMappingError
from mock import Mock
import pytest

from bravado.mapping.operation import Operation
from bravado.mapping.param import Param, get_param_type_spec


def test_location_is_body(empty_swagger_spec):
    param_spec = {
        'name': 'body',
        'in': 'body',
        'description': 'ID of pet that needs to be updated',
        'required': True,
        'schema': {
            'type': 'string'
        }
    }
    param = Param(empty_swagger_spec, Mock(spec=Operation), param_spec)
    assert param_spec['schema'] == get_param_type_spec(param)


def test_location_is_not_body(empty_swagger_spec):
    for location in ('path', 'query', 'header', 'formData',):
        param_spec = {
            'name': 'petId',
            'in': location,
            'description': 'ID of pet that needs to be updated',
            'required': True,
            'type': 'string',
        }
        param = Param(empty_swagger_spec, Mock(spec=Operation), param_spec)
        assert param_spec == get_param_type_spec(param)


def test_location_unknown(empty_swagger_spec):
    param_spec = {
        'in': 'foo',
    }
    param = Param(empty_swagger_spec, Mock(spec=Operation), param_spec)

    with pytest.raises(SwaggerMappingError) as excinfo:
        get_param_type_spec(param)
    assert 'location foo' in str(excinfo)
