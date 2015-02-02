#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
# Copyright (c) 2014, Yelp, Inc.
#

"""Swagger client tests to validate resource 'model_dict's

A sample 'model_dict' is listed below in models list.

{
    "apiVersion": "1.0.0",
    "swaggerVersion": "1.2",
    "apis": [...],
    "models": {
        "Pet": {
            "id": "Pet",
            "required": [
                "id",
                "name"
            ],
            "properties": {
                "id": {
                    "type": "integer",
                    "format": "int64",
                    "description": "unique identifier for the pet",
                },
                "category": {
                    "$ref": "Category"
                },
                "name": {
                    "type": "string"
                },
                "photoUrls": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    }
                },
                "status": {
                    "type": "string",
                    "description": "pet status in the store",
                }
            }
        }
    }
}
"""

from bravado.compat import json
import unittest

import httpretty
import pytest

from bravado.client import SwaggerClient
from bravado.exception import SwaggerError


@pytest.mark.xfail(reason='Re-write when Resource ported over to swagger 2.0')
class ResourceTest(unittest.TestCase):

    def setUp(self):
        self.models = {
            "School": {
                "id": "School",
                "properties": {
                    "name": {
                        "type": "string"
                    }
                },
                "required": ["name"]
            },
            "User": {
                "id": "User",
                "properties": {
                    "id": {
                        "type": "integer",
                        "format": "int64"
                    },
                    "schools": {
                        "type": "array",
                        "items": {
                            "$ref": "School"
                        }
                    }
                },
                "required": ["id"]
            }
        }
        self.sample_model = {
            "id": 42,
            "schools": [
                {"name": "School1"},
                {"name": "School2"}
            ]
        }
        operation = {
            "method": "GET",
            "nickname": "testHTTP",
            "type": "User",
            "parameters": []
        }
        operation_post = {
            "method": "POST",
            "nickname": "testHTTPPost",
            "type": "void",
            "parameters": []
        }
        api = {
            "path": "/test_http",
            "operations": [operation]
        }
        api_post = {
            "path": "/test_http",
            "operations": [operation_post]
        }
        self.response = {
            "swaggerVersion": "1.2",
            "basePath": "/",
            "apis": [api, api_post],
            "models": self.models
        }

    def register_urls(self):
        httpretty.register_uri(
            httpretty.GET, "http://localhost/api-docs",
            body=json.dumps({
                "swaggerVersion": "1.2",
                "apis": [{
                    "path": "/api_test"
                }]
            }))
        httpretty.register_uri(
            httpretty.GET, "http://localhost/api-docs/api_test",
            body=json.dumps(self.response))

        httpretty.register_uri(
            httpretty.POST, "http://localhost/test_http",
            body="")

    ###########################################################################
    # Validate the correctness of Complex (non-primitive) Type response
    # ie. if a 'School' is expected to be returned,
    # then it in fact should be a 'School'
    # API call is triggered in below tests and the response type is validated
    ###########################################################################

    @httpretty.activate
    def test_success_on_complex_operation_response_type(self):
        self.register_urls()
        httpretty.register_uri(
            httpretty.GET, "http://localhost/test_http",
            body=json.dumps(self.sample_model))
        resource = SwaggerClient.from_url(
            u'http://localhost/api-docs').api_test
        resp = resource.testHTTP().result()
        models = resource.testHTTP._models
        User = models['User']
        School = models['School']
        self.assertTrue(isinstance(resp, User))
        [self.assertTrue(isinstance(x, School)) for x in resp.schools]
        self.assertEqual(User(id=42, schools=[School(
            name="School1"), School(name="School2")]), resp)

    @httpretty.activate
    def test_error_on_missing_required_type_instead_of_complex_type(self):
        self.register_urls()
        self.sample_model.pop("id")
        httpretty.register_uri(
            httpretty.GET, "http://localhost/test_http",
            body=json.dumps(self.sample_model))
        self.assertRaises(AssertionError, SwaggerClient.from_url(
            u'http://localhost/api-docs').api_test.testHTTP().result)

    @httpretty.activate
    def test_success_on_extra_field_in_complex_type(self):
        self.register_urls()
        self.sample_model["extra"] = 42
        httpretty.register_uri(
            httpretty.GET, "http://localhost/test_http",
            body=json.dumps(self.sample_model))
        result = SwaggerClient.from_url(
            u'http://localhost/api-docs').api_test.testHTTP().result()
        self.assertEqual(result._raw["extra"], 42)

    @httpretty.activate
    def test_error_on_wrong_type_instead_of_complex_type(self):
        self.register_urls()
        httpretty.register_uri(
            httpretty.GET, "http://localhost/test_http",
            body='"NOT_COMPLEX_TYPE"')
        self.assertRaises(TypeError, SwaggerClient.from_url(
            u'http://localhost/api-docs').api_test.testHTTP().result)

    @httpretty.activate
    def test_error_on_wrong_type_inside_complex_type(self):
        self.register_urls()
        self.sample_model["id"] = "Not Integer"
        httpretty.register_uri(
            httpretty.GET, "http://localhost/test_http",
            body=json.dumps(self.sample_model))
        self.assertRaises(TypeError, SwaggerClient.from_url(
            u'http://localhost/api-docs').api_test.testHTTP().result)

    @httpretty.activate
    def test_error_on_wrong_type_inside_nested_complex_type_2(self):
        self.register_urls()
        self.sample_model["schools"][0] = "Not School"
        httpretty.register_uri(
            httpretty.GET, "http://localhost/test_http",
            body=json.dumps(self.sample_model))
        self.assertRaises(TypeError, SwaggerClient.from_url(
            u'http://localhost/api-docs').api_test.testHTTP().result)

    @httpretty.activate
    def test_error_on_missing_type_inside_nested_complex_type_1(self):
        self.register_urls()
        self.sample_model["schools"][0] = {}  # Omit 'name'
        httpretty.register_uri(
            httpretty.GET, "http://localhost/test_http",
            body=json.dumps(self.sample_model))
        self.assertRaises(AssertionError, SwaggerClient.from_url(
            u'http://localhost/api-docs').api_test.testHTTP().result)

    @httpretty.activate
    def test_error_on_passing_model_in_param_query(self):
        """Only primitive types are allowed in path or query
        """
        query_parameter = {
            "paramType": "query",
            "name": "test_param",
            "type": "School",
        }
        self.response["apis"][0]["operations"][0]["parameters"] = [
            query_parameter]
        self.register_urls()
        resource = SwaggerClient.from_url(
            u'http://localhost/api-docs').api_test
        school = resource.testHTTP._models['School']
        self.assertRaises(TypeError, resource.testHTTP, test_param=school)

    @httpretty.activate
    def test_alllow_null_in_response_body_if_allow_null_is_given(self):
        self.register_urls()
        self.sample_model["schools"].append(None)
        httpretty.register_uri(
            httpretty.GET, "http://localhost/test_http",
            body=json.dumps(self.sample_model))
        resource = SwaggerClient.from_url(
            u'http://localhost/api-docs').api_test
        resp = resource.testHTTP().result(allow_null=True)
        self.assertTrue(isinstance(resp, resource.testHTTP._models['User']))

    @httpretty.activate
    def test_alllow_null_as_response_if_allow_null_is_given(self):
        self.register_urls()
        httpretty.register_uri(
            httpretty.GET, "http://localhost/test_http",
            body=json.dumps(None))
        resource = SwaggerClient.from_url(
            u'http://localhost/api-docs').api_test
        resource.testHTTP().result(allow_null=True)

    @httpretty.activate
    def test_error_if_response_body_has_null_and_allow_null_not_given(self):
        self.register_urls()
        self.sample_model["schools"].append(None)
        httpretty.register_uri(
            httpretty.GET, "http://localhost/test_http",
            body=json.dumps(self.sample_model))
        resource = SwaggerClient.from_url(
            u'http://localhost/api-docs').api_test
        self.assertRaises(TypeError, resource.testHTTP().result)

    @httpretty.activate
    def test_error_if_response_is_null_and_allow_null_not_given(self):
        self.register_urls()
        httpretty.register_uri(
            httpretty.GET, "http://localhost/test_http",
            body=json.dumps(None))
        resource = SwaggerClient.from_url(
            u'http://localhost/api-docs').api_test
        self.assertRaises(TypeError, resource.testHTTP().result)

    @httpretty.activate
    def test_remove_null_values_when_convert_to_flat_dict(self):
        self.register_urls()
        httpretty.register_uri(
            httpretty.GET, "http://localhost/test_http",
            body=json.dumps(self.sample_model))
        resource = SwaggerClient.from_url(
            u'http://localhost/api-docs').api_test
        models = resource.testHTTP._models
        User = models['User']
        School = models['School']
        user = User(schools=[School(name='a'), None])
        self.assertEqual(None, user.schools[1])
        self.assertEqual([{'name': 'a'}], user._flat_dict()['schools'])

    #################################################
    # Model Py instance sent in request body
    ################################################

    @httpretty.activate
    def test_success_model_in_param_body_converts_to_dict(self):
        query_parameter = {
            "paramType": "body",
            "name": "body",
            "type": "User",
        }
        self.response["apis"][1]["operations"][0]["parameters"] = [
            query_parameter]
        self.register_urls()
        resource = SwaggerClient.from_url(
            u'http://localhost/api-docs').api_test
        models = resource.testHTTP._models
        User = models['User']
        School = models['School']
        # Also test all None items are removed from array list
        user = User(id=42, schools=[School(name='s1'), None])
        future = resource.testHTTPPost(body=user)
        self.assertEqual(
            json.dumps({'id': 42, 'schools': [{'name': 's1'}]}),
            future._request.request.data,
        )

    @httpretty.activate
    def test_removal_of_none_attributes_from_param_body_model(self):
        query_parameter = {
            "paramType": "body",
            "name": "body",
            "type": "User",
        }
        self.response["apis"][1]["operations"][0]["parameters"] = [
            query_parameter]
        self.response["models"]["User"]["properties"]["school"] = {
            "$ref": "School"}
        self.register_urls()
        resource = SwaggerClient.from_url(
            u'http://localhost/api-docs').api_test
        user = resource.testHTTP._models['User'](id=42)
        future = resource.testHTTPPost(body=user)
        # Removed the 'school': None - key, value pair from dict
        self.assertEqual(
            json.dumps({'id': 42, 'schools': []}),
            future._request.request.data,
        )

    @httpretty.activate
    def test_error_on_finding_required_attributes_none(self):
        query_parameter = {
            "paramType": "body",
            "name": "body",
            "type": "User",
        }
        self.response["apis"][1]["operations"][0]["parameters"] = [
            query_parameter]
        self.response["models"]["User"]["properties"]["school"] = {
            "$ref": "School"}
        self.response["models"]["User"]["required"] = ["school"]
        self.register_urls()
        resource = SwaggerClient.from_url(
            u'http://localhost/api-docs').api_test
        user = resource.testHTTP._models['User'](id=42)
        self.assertRaises(AttributeError, resource.testHTTPPost, body=user)

    #################################################
    # Model JSON sent in request body
    ################################################

    @httpretty.activate
    def test_content_type_as_json_if_complex_type_in_body(self):
        query_parameter = {
            "paramType": "body",
            "name": "body",
            "type": "School",
        }
        school = {"name": "temp"}
        self.response["apis"][1]["operations"][0]["type"] = "School"
        self.response["apis"][1]["operations"][0]["parameters"] = [
            query_parameter]
        self.register_urls()
        httpretty.register_uri(
            httpretty.GET, "http://localhost/test_http",
            body=json.dumps(school))
        resource = SwaggerClient.from_url(
            u'http://localhost/api-docs').api_test
        resource.testHTTPPost(body=school).result()
        self.assertEqual("application/json", httpretty.last_request().headers[
            'content-type'])

    @httpretty.activate
    def test_content_type_not_present_if_only_primitive_type_in_body(self):
        query_parameter = {
            "paramType": "body",
            "name": "body",
            "type": "integer",
        }
        self.response["apis"][1]["operations"][0]["parameters"] = [
            query_parameter]
        self.register_urls()
        httpretty.register_uri(
            httpretty.GET, "http://localhost/test_http",
            body=json.dumps({'id': 1}))
        client = SwaggerClient.from_url(u'http://localhost/api-docs').api_test
        client.testHTTPPost(body=42).result()
        self.assertFalse('content-type' in httpretty.last_request().headers)


if __name__ == '__main__':
    unittest.main()
