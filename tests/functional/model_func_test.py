"""
Functional tests related to passing models in req/response
"""
import httpretty
from jsonschema.exceptions import ValidationError
import pytest

from bravado.compat import json
from bravado.client import SwaggerClient
from tests.functional.conftest import register_spec, register_get, API_DOCS_URL


@pytest.fixture
def sample_model():
    return {
        "id": 42,
        "schools": [
            {"name": "School1"},
            {"name": "School2"}
        ]
    }


@pytest.fixture
def swagger_dict():
    models = {
        "School": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string"
                }
            },
            "required": ["name"]
        },
        "User": {
            "type": "object",
            "properties": {
                "id": {
                    "type": "integer",
                    "format": "int64"
                },
                "schools": {
                    "type": "array",
                    "items": {
                        "$ref": "#/definitions/School"
                    }
                }
            },
            "required": ["id"]
        }
    }
    operation = {
        "tags": ["api_test"],
        "operationId": "testHTTP",
        "parameters": [],
        "responses": {
            "200": {
                "description": "blah",
                "schema": {
                    "$ref": "#/definitions/User",
                }
            }
        }
    }
    operation_post = {
        "tags": ["api_test"],
        "operationId": "testHTTPPost",
        "parameters": [],
        "responses": {
            "200": {
                "description": "Successs"
            }
        }
    }
    paths = {
        "/test_http": {
            'get': operation,
            'post': operation_post,
        },
    }
    return {
        "swagger": "2.0",
        "info": {
            "version": "1.0.0",
            "title": "Simple"
        },
        "basePath": "/",
        "paths": paths,
        "definitions": models
    }


@pytest.mark.parametrize(
    'spec_type',
    (
        ('json',),
        ('yaml',),
    )
)
def test_model_in_response(
        httprettified, swagger_dict, sample_model, spec_type):
    register_spec(swagger_dict, spec_type=spec_type)
    register_get("http://localhost/test_http", body=json.dumps(sample_model))
    client = SwaggerClient.from_url(API_DOCS_URL)
    result = client.api_test.testHTTP().result()
    User = client.get_model('User')
    School = client.get_model('School')
    assert isinstance(result, User)
    for school in result.schools:
        assert isinstance(school, School)
    assert User(
        id=42,
        schools=[
            School(name="School1"),
            School(name="School2")
        ]) == result


def test_model_missing_required_property_in_response_raises_ValidationError(
        httprettified, swagger_dict, sample_model):
    register_spec(swagger_dict)
    sample_model.pop("id")
    register_get("http://localhost/test_http", body=json.dumps(sample_model))
    with pytest.raises(ValidationError) as excinfo:
        SwaggerClient.from_url(API_DOCS_URL).api_test.testHTTP().result()
    assert "'id' is a required property" in str(excinfo.value)


def test_additionalProperty_in_model_in_response(
        httprettified, swagger_dict, sample_model):
    register_spec(swagger_dict)
    sample_model["extra"] = 42
    register_get("http://localhost/test_http", body=json.dumps(sample_model))
    resource = SwaggerClient.from_url(API_DOCS_URL).api_test
    result = resource.testHTTP().result()
    assert result.extra == 42


def test_invalid_type_in_response_raises_ValidationError(
        httprettified, swagger_dict, sample_model):
    register_spec(swagger_dict)
    register_get("http://localhost/test_http", body='"NOT_COMPLEX_TYPE"')
    with pytest.raises(ValidationError) as excinfo:
        SwaggerClient.from_url(API_DOCS_URL).api_test.testHTTP().result()
    assert "'NOT_COMPLEX_TYPE' is not of type" in str(excinfo.value)


def test_error_on_wrong_type_inside_complex_type(
        httprettified, swagger_dict, sample_model):
    register_spec(swagger_dict)
    sample_model["id"] = "Not Integer"
    register_get("http://localhost/test_http", body=json.dumps(sample_model))
    with pytest.raises(ValidationError) as excinfo:
        SwaggerClient.from_url(API_DOCS_URL).api_test.testHTTP().result()
    assert "'Not Integer' is not of type" in str(excinfo.value)


def test_error_on_missing_type_in_model(
        httprettified, swagger_dict, sample_model):
    register_spec(swagger_dict)
    sample_model["schools"][0] = {}  # Omit 'name'
    register_get("http://localhost/test_http", body=json.dumps(sample_model))
    with pytest.raises(ValidationError) as excinfo:
        SwaggerClient.from_url(API_DOCS_URL).api_test.testHTTP().result()
    assert "'name' is a required property" in str(excinfo.value)


def test_model_in_body_of_request(httprettified, swagger_dict, sample_model):
    param_spec = {
        "in": "body",
        "name": "body",
        "schema": {
            "$ref": "#/definitions/User"
        }
    }
    swagger_dict["paths"]["/test_http"]['post']["parameters"] = [param_spec]
    register_spec(swagger_dict)
    httpretty.register_uri(httpretty.POST, "http://localhost/test_http")
    client = SwaggerClient.from_url(API_DOCS_URL)
    resource = client.api_test
    User = client.get_model('User')
    School = client.get_model('School')
    user = User(id=42, schools=[School(name='s1')])
    resource.testHTTPPost(body=user).result()
    body = json.loads(httpretty.last_request().body)
    assert {'schools': [{'name': 's1'}], 'id': 42} == body
