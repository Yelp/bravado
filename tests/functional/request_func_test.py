"""
Request related functional tests
"""
import httpretty
from six.moves import cStringIO
from six.moves.urllib import parse as urlparse

from bravado.client import SwaggerClient
from tests.functional.conftest import register_spec, API_DOCS_URL, register_get


def test_form_params_in_request(httprettified, swagger_dict):
    param1_spec = {
        "in": "formData",
        "name": "param_id",
        "type": "integer"
    }
    param2_spec = {
        "in": "formData",
        "name": "param_name",
        "type": "string"
    }
    path_spec = swagger_dict['paths']['/test_http']
    path_spec['post'] = path_spec.pop('get')
    path_spec['post']['parameters'] = [param1_spec, param2_spec]
    register_spec(swagger_dict)
    httpretty.register_uri(httpretty.POST, "http://localhost/test_http?")
    resource = SwaggerClient.from_url(API_DOCS_URL).api_test
    resource.testHTTP(param_id=42, param_name='foo').result()
    content_type = httpretty.last_request().headers['content-type']
    assert 'application/x-www-form-urlencoded' == content_type
    body = urlparse.parse_qs(httpretty.last_request().body)
    assert {b'param_name': [b'foo'], b'param_id': [b'42']} == body


def test_file_upload_in_request(httprettified, swagger_dict):
    param1_spec = {
        "in": "formData",
        "name": "param_id",
        "type": "integer"
    }
    param2_spec = {
        "in": "formData",
        "name": "file_name",
        "type": "file"
    }
    path_spec = swagger_dict['paths']['/test_http']
    path_spec['post'] = path_spec.pop('get')
    path_spec['post']['parameters'] = [param1_spec, param2_spec]
    path_spec['post']['consumes'] = ['multipart/form-data']
    register_spec(swagger_dict)
    httpretty.register_uri(httpretty.POST, "http://localhost/test_http?")
    resource = SwaggerClient.from_url(API_DOCS_URL).api_test
    resource.testHTTP(param_id=42, file_name=cStringIO('boo')).result()
    content_type = httpretty.last_request().headers['content-type']

    assert content_type.startswith('multipart/form-data')
    assert b"42" in httpretty.last_request().body
    assert b"boo" in httpretty.last_request().body


def test_parameter_in_path_of_request(httprettified, swagger_dict):
    path_param_spec = {
        "in": "path",
        "name": "param_id",
        "type": "string"
    }
    paths_spec = swagger_dict['paths']
    paths_spec['/test_http/{param_id}'] = paths_spec.pop('/test_http')
    paths_spec['/test_http/{param_id}']['get']['parameters'].append(
        path_param_spec)
    register_spec(swagger_dict)
    register_get('http://localhost/test_http/42?test_param=foo')
    resource = SwaggerClient.from_url(API_DOCS_URL).api_test
    assert resource.testHTTP(test_param="foo", param_id="42").result() is None


def test_default_value_not_in_request(httprettified, swagger_dict):
    # Default should be applied on the server side so no need to send it in
    # the request.
    swagger_dict['paths']['/test_http']['get']['parameters'][0]['default'] = 'X'
    register_spec(swagger_dict)
    register_get("http://localhost/test_http?")
    resource = SwaggerClient.from_url(API_DOCS_URL).api_test
    resource.testHTTP().result()
    assert 'test_param' not in httpretty.last_request().querystring


def test_array_with_collection_format_in_path_of_request(
        httprettified, swagger_dict):
    path_param_spec = {
        'in': 'path',
        'name': 'param_ids',
        'type': 'array',
        'items': {
            'type': 'integer'
        },
        'collectionFormat': 'csv',
    }
    swagger_dict['paths']['/test_http/{param_ids}'] = \
        swagger_dict['paths'].pop('/test_http')
    swagger_dict['paths']['/test_http/{param_ids}']['get']['parameters'] = \
        [path_param_spec]
    register_spec(swagger_dict)
    register_get('http://localhost/test_http/40,41,42')
    resource = SwaggerClient.from_url(API_DOCS_URL).api_test
    assert resource.testHTTP(param_ids=[40, 41, 42]).result() is None
