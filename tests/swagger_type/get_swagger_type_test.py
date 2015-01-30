import pytest

from bravado.exception import SwaggerError
from bravado.swagger_type import get_swagger_type


def test_type_only():
    schema_obj = {
        'type': 'integer',
    }
    assert 'integer' == get_swagger_type(schema_obj)


def test_format_and_type():
    schema_obj = {
        'type': 'integer',
        'format': 'int64',
    }
    assert 'integer:int64' == get_swagger_type(schema_obj)


def test_array():
    schema_obj = {
        'type': 'array',
        'items': {
            'type': 'string',
        }
    }
    assert 'array:string' == get_swagger_type(schema_obj)


def test_ref():
    schema_obj = {
        '$ref': '#/definitions/Foo',
    }
    assert '#/definitions/Foo' == get_swagger_type(schema_obj)


def test_missing_type_raises_error():
    with pytest.raises(SwaggerError) as excinfo:
        get_swagger_type({'TyP3': 'string'})
    assert 'No proper type' in str(excinfo.value)
