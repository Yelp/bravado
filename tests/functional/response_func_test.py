"""
Response related functional tests
"""
import datetime

from jsonschema.exceptions import ValidationError
import pytest
from requests import HTTPError

from bravado.client import SwaggerClient
from bravado.compat import json
from tests.functional.conftest import register_spec, register_get, API_DOCS_URL


def test_500_error_raises_HTTPError(httprettified, swagger_dict):
    register_spec(swagger_dict)
    register_get('http://localhost/test_http?test_param=foo', status=500)
    resource = SwaggerClient.from_url(API_DOCS_URL).api_test
    with pytest.raises(HTTPError) as excinfo:
        resource.testHTTP(test_param='foo').result()
    assert '500 Server Error' in str(excinfo.value)


def test_primitive_types_returned_in_response(httprettified, swagger_dict):
    rtypes = {
        'string': '"test"',
        'integer': 42,
        'number': 3.4,
        'boolean': True
    }
    for rtype, rvalue in rtypes.iteritems():
        response_specs = swagger_dict['paths']['/test_http']['get']['responses']
        response_specs['200']['schema'] = {'type': rtype}
        register_spec(swagger_dict)
        register_get(
            'http://localhost/test_http?test_param=foo',
            body=json.dumps(rvalue))
        resource = SwaggerClient.from_url(API_DOCS_URL).api_test
        status, result = resource.testHTTP(test_param="foo").result()
        assert rvalue == result


def test_invalid_primitive_types_in_response_raises_ValidationError(
        httprettified, swagger_dict):
    rtypes = {
        'string': 42,
        'integer': 3.4,
        'number': 'foo',
        'boolean': '"NOT_BOOL"'
    }
    for rtype, rvalue in rtypes.iteritems():
        response_specs = swagger_dict['paths']['/test_http']['get']['responses']
        response_specs['200']['schema'] = {'type': rtype}
        register_spec(swagger_dict)
        register_get(
            'http://localhost/test_http?test_param=foo',
            body=json.dumps(rvalue))
        resource = SwaggerClient.from_url(API_DOCS_URL).api_test
        with pytest.raises(ValidationError) as excinfo:
            resource.testHTTP(test_param="foo").result()
        assert 'is not of type' in str(excinfo.value)


def test_unstructured_json_in_response(httprettified, swagger_dict):
    response_specs = swagger_dict['paths']['/test_http']['get']['responses']
    response_specs['200']['schema'] = {
        'type': 'object',
        'additionalProperties': True,
    }
    register_spec(swagger_dict)
    register_get(
        'http://localhost/test_http?test_param=foo',
        body='{"some_foo": "bar"}')
    resource = SwaggerClient.from_url(API_DOCS_URL).api_test
    status, result = resource.testHTTP(test_param="foo").result()
    assert {'some_foo': 'bar'} == result


def test_date_format_in_reponse(httprettified, swagger_dict):
    response_specs = swagger_dict['paths']['/test_http']['get']['responses']
    response_specs['200']['schema'] = {
        'type': 'string',
        'format': 'date',
    }
    register_spec(swagger_dict)
    register_get(
        'http://localhost/test_http?test_param=foo',
        body=json.dumps("2014-06-10"))
    resource = SwaggerClient.from_url(API_DOCS_URL).api_test
    status, result = resource.testHTTP(test_param="foo").result()
    assert result == datetime.date(2014, 6, 10)


def test_array_in_response(httprettified, swagger_dict):
    response_specs = swagger_dict['paths']['/test_http']['get']['responses']
    response_specs['200']['schema'] = {
        'type': 'array',
        'items': {
            'type': 'string',
        },
    }
    register_spec(swagger_dict)
    expected_array = ['inky', 'dinky', 'doo']
    register_get(
        'http://localhost/test_http?test_param=foo',
        body=json.dumps(expected_array))
    resource = SwaggerClient.from_url(API_DOCS_URL).api_test
    status, result = resource.testHTTP(test_param="foo").result()
    assert  expected_array == result
