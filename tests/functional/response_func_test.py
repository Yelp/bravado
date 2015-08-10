"""
Response related functional tests
"""
import datetime
import functools

from jsonschema.exceptions import ValidationError
import pytest

from bravado.client import SwaggerClient
from bravado.compat import json
from bravado.exception import HTTPError
from tests.functional.conftest import register_spec, register_get, API_DOCS_URL


register_test_http = functools.partial(
    register_get,
    'http://localhost/test_http?test_param=foo')


def assert_result(expected_result):
    resource = SwaggerClient.from_url(API_DOCS_URL).api_test
    assert expected_result == resource.testHTTP(test_param='foo').result()


def assert_raises_and_matches(exc_type, match_str):
    resource = SwaggerClient.from_url(API_DOCS_URL).api_test
    with pytest.raises(exc_type) as excinfo:
        resource.testHTTP(test_param='foo').result()
    assert match_str in str(excinfo.value)


def test_500_error_raises_HTTPError(httprettified, swagger_dict):
    register_spec(swagger_dict)
    register_get('http://localhost/test_http?test_param=foo', status=500)
    assert_raises_and_matches(HTTPError, '500 Internal Server Error')


def test_primitive_types_returned_in_response(httprettified, swagger_dict):
    rtypes = {
        'string': '"test"',
        'integer': 42,
        'number': 3.4,
        'boolean': True
    }
    for rtype, rvalue in rtypes.items():
        register_spec(swagger_dict, {'type': rtype})
        register_test_http(body=json.dumps(rvalue))
        assert_result(rvalue)


def test_invalid_primitive_types_in_response_raises_ValidationError(
        httprettified, swagger_dict):
    rtypes = {
        'string': 42,
        'integer': 3.4,
        'number': 'foo',
        'boolean': '"NOT_BOOL"'
    }
    for rtype, rvalue in rtypes.items():
        register_spec(swagger_dict, {'type': rtype})
        register_test_http(body=json.dumps(rvalue))
        assert_raises_and_matches(ValidationError, 'is not of type')


def test_unstructured_json_in_response(httprettified, swagger_dict):
    response_spec = {'type': 'object', 'additionalProperties': True}
    register_spec(swagger_dict, response_spec)
    register_test_http(body='{"some_foo": "bar"}')
    assert_result({'some_foo': 'bar'})


def test_date_format_in_reponse(httprettified, swagger_dict):
    response_spec = {'type': 'string', 'format': 'date'}
    register_spec(swagger_dict, response_spec)
    register_test_http(body=json.dumps("2014-06-10"))
    assert_result(datetime.date(2014, 6, 10))


def test_array_in_response(httprettified, swagger_dict):
    response_spec = {
        'type': 'array',
        'items': {
            'type': 'string',
        },
    }
    register_spec(swagger_dict, response_spec)
    expected_array = ['inky', 'dinky', 'doo']
    register_test_http(body=json.dumps(expected_array))
    assert_result(expected_array)
