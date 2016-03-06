import functools
import json

import httpretty
import pytest
import yaml


API_DOCS_URL = "http://localhost/api-docs"

# Convenience for httpretty.register_uri(httpretty.GET, **kwargs)
register_get = functools.partial(httpretty.register_uri, httpretty.GET)


def register_spec(swagger_dict, response_spec=None, spec_type='json'):
    if response_spec is not None:
        response_specs = swagger_dict['paths']['/test_http']['get']['responses']
        response_specs['200']['schema'] = response_spec

    if spec_type == 'yaml':
        serialize_function = yaml.dump
        content_type = 'application/yaml'
    else:
        serialize_function = json.dumps
        content_type = 'application/json'
    headers = 'Content-Type: {0}'.format(content_type)
    register_get(
        API_DOCS_URL,
        body=serialize_function(swagger_dict),
        headers=headers,
    )


@pytest.fixture
def swagger_dict():
    parameter = {
        "in": "query",
        "name": "test_param",
        "type": "string"
    }
    responses = {
        "200": {
            "description": "Success"
        }
    }
    operation = {
        "operationId": "testHTTP",
        "parameters": [parameter],
        "responses": responses,
        "tags": ["api_test"],
    }
    paths = {
        "/test_http": {
            "get": operation
        }
    }
    return {
        "swagger": "2.0",
        "info": {
            "version": "1.0.0",
            "title": "Simple"
        },
        "basePath": "/",
        "paths": paths
    }


@pytest.fixture
def httprettified(request):
    """
    pytest style fixture to activate/deactive httpretty so that you get the
    benefit of the @httpretty.activate decoratator without having to use it.

    Basically, this won't work:

        @httpretty.activate
        def test_foo(some_pytest_fixture):
            pass

    Use this instead:

        def test_foo(httprettified, some_pytest_fixture):
            # interactions with httpretty occur as if you'd decorated
            # this function with @httpretty.activate
            httpretty.register_uri(...)

    If you're passing multiple fixtures to the test that rely on httpretty
    being activated, make sure that `httprettified` is before all the other
    fixtures that depend on it.

    :param request: This is a pytest (confusingly named) param. Don't worry
        about it.
    """
    # TODO: move to test util package
    httpretty.reset()
    httpretty.enable()

    def fin():
        httpretty.disable()

    request.addfinalizer(fin)
