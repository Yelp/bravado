#!/usr/bin/env python

#
# Copyright (c) 2014, Yelp, Inc.
#

"""Swagger client tests to validate resource api 'operation'

A sample 'peration' is listed below in 'operations' list.
{
    ...
    apis": [
    {
        "path": "/pet/{petId}",
        "operations": [
            {
                "method": "GET",
                "summary": "Find pet by ID",
                "notes": "Returns a pet based on ID",
                "type": "Pet",
                "nickname": "getPetById",
                "authorizations": { },
                "parameters": [
                    {
                        "name": "petId",
                        "description": "ID of pet that needs to be fetched",
                        "required": true,
                        "type": "integer",
                        "format": "int64",
                        "paramType": "path",
                        "allowMultiple": false,
                    }
                ],
                "responseMessages": [
                    {
                        "code": 400,
                        "message": "Invalid ID supplied"
                    }
                ]
            }
        ]
    }]
    ...
}
"""

import json
import unittest

import httpretty

from swaggerpy.client import SwaggerClient
from swaggerpy.processors import SwaggerError


class ResourceOperationTest(unittest.TestCase):
    def setUp(self):
        self.parameter = {
            "paramType": "query",
            "name": "test_param",
            "type": "string"
        }
        operation = {
            "method": "GET",
            "nickname": "testHTTP",
            "type": "void",
            "parameters": [self.parameter]
        }
        api = {
            "path": "/test_http",
            "operations": [operation]
        }
        self.response = {
            "swaggerVersion": "1.2",
            "basePath": "/",
            "apis": [api]
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

    @httpretty.activate
    def test_error_on_missing_attr(self):
        def iterate_test(field):
            self.response["apis"][0]["operations"][0].pop(field)
            self.register_urls()
            self.assertRaises(SwaggerError, SwaggerClient, u'http://localhost/api-docs')
        [iterate_test(field) for field in ('method', 'nickname', 'type', 'parameters')]

    # Validate param in operation
    #############################
    # ToDo: Check correctness if $ref is passed (and no type)

    @httpretty.activate
    def test_error_on_missing_attr_in_parameter(self):
        def iterate_test(field):
            self.response["apis"][0]["operations"][0]["parameters"][0].pop(field)
            self.register_urls()
            self.assertRaises(SwaggerError, SwaggerClient, u'http://localhost/api-docs')
        [iterate_test(field) for field in ('type', 'paramType', 'name')]

    @httpretty.activate
    def test_error_on_missing_items_param_in_array_parameter(self):
        self.response["apis"][0]["operations"][0]["type"] = "array"
        self.register_urls()
        self.assertRaises(SwaggerError, SwaggerClient, u'http://localhost/api-docs')

    @httpretty.activate
    def test_error_on_wrong_attr_type_in_parameter(self):
        self.response["apis"][0]["operations"][0]["parameters"][0]["type"] = "WRONG_TYPE"
        self.register_urls()
        self.assertRaises(SwaggerError, SwaggerClient, u'http://localhost/api-docs')

    @httpretty.activate
    def test_error_on_wrong_attr_type_in_array_parameter(self):
        self.response["apis"][0]["operations"][0]["parameters"][0]["type"] = "array"
        self.response["apis"][0]["operations"][0]["parameters"][0]["items"] = {"type": "WRONG_TYPE"}
        self.register_urls()
        self.assertRaises(TypeError, SwaggerClient, u'http://localhost/api-docs')

    @httpretty.activate
    def test_error_on_missing_param_in_error_response(self):
        msg = {"code": 400, "message": "some message"}

        def iterate_test(field):
            self.response["apis"][0]["operations"][0]["responseMessages"] = [msg]
            self.response["apis"][0]["operations"][0]["responseMessages"][0].pop(field)
            self.register_urls()
            self.assertRaises(SwaggerError, SwaggerClient, u'http://localhost/api-docs')
        [iterate_test(field) for field in ('code', 'message')]

    # Validate paramType of parameters - path, query, body
    ######################################################

    @httpretty.activate
    def test_success_on_get_with_path_and_query_params(self):
        query_parameter = self.parameter
        path_parameter = {
            "paramType": "path",
            "name": "param_id",
            "type": "string"
        }
        self.response["apis"][0]["path"] = "/params/{param_id}/test_http"
        self.response["apis"][0]["operations"][0]["parameters"] = [query_parameter, path_parameter]
        self.register_urls()
        httpretty.register_uri(
            httpretty.GET, "http://localhost/params/42/test_http?test_param=foo",
            body='')
        resource = SwaggerClient(u'http://localhost/api-docs').api_test
        resp = resource.testHTTP(test_param="foo", param_id="42").result()
        self.assertEqual(None, resp)

    @httpretty.activate
    def test_success_on_get_with_array_in_path_and_query_params(self):
        query_parameter = {
            "paramType": "query",
            "name": "test_params",
            "type": "array",
            "items": {
                "type": "string"}}
        path_parameter = {
            "paramType": "path",
            "name": "param_ids",
            "type": "array",
            "items": {
                "type": "integer"}}
        self.response["apis"][0]["path"] = "/params/{param_ids}/test_http"
        self.response["apis"][0]["operations"][0]["parameters"] = [query_parameter, path_parameter]
        self.register_urls()
        httpretty.register_uri(
            httpretty.GET, "http://localhost/params/40,41,42/test_http?test_param=foo,bar",
            body='')
        resource = SwaggerClient(u'http://localhost/api-docs').api_test
        resp = resource.testHTTP(test_params=["foo", "bar"], param_ids=[40, 41, 42]).result()
        self.assertEqual(None, resp)

    """
    # ToDo: Wrong param type not being checked as of now...
    # Commented test is expected to fail
    @httpretty.activate
    def test_error_on_get_with_wrong_type_param(self):
        query_parameter = {
            "paramType": "query",
            "name": "test_param",
            "type": "integer"
        }
        self.response["apis"][0]["operations"][0]["parameters"] = [query_parameter]
        self.register_urls()
        resource = SwaggerClient(u'http://localhost/api-docs').api_test
        self.assertRaises(TypeError, resource.testHTTP, test_param="NOT_INTEGER")
    """

    @httpretty.activate
    def test_success_on_post_with_path_query_and_body_params(self):
        query_parameter = self.parameter
        path_parameter = {
            "paramType": "path",
            "name": "param_id",
            "type": "string"
        }
        body_parameter = {
            "paramType": "body",
            "name": "body",
            "type": "string"
        }
        self.response["apis"][0]["path"] = "/params/{param_id}/test_http"
        self.response["apis"][0]["operations"][0]["method"] = "POST"
        self.response["apis"][0]["operations"][0]["parameters"] = [query_parameter,
                                                                   path_parameter,
                                                                   body_parameter]
        self.register_urls()
        httpretty.register_uri(
            httpretty.POST, "http://localhost/params/42/test_http?test_param=foo",
            body='')
        resource = SwaggerClient(u'http://localhost/api-docs').api_test
        resp = resource.testHTTP(test_param="foo", param_id="42", body="some_test").result()
        self.assertEqual('application/json', httpretty.last_request().headers['content-type'])
        self.assertEqual('some_test', httpretty.last_request().body)
        self.assertEqual(None, resp)

    @httpretty.activate
    def test_success_on_post_with_array_in_body_params(self):
        body_parameter = {
            "paramType": "body",
            "name": "body",
            "type": "array",
            "items": {
                "type": "string"
            }
        }
        self.response["apis"][0]["operations"][0]["parameters"] = [body_parameter]
        self.response["apis"][0]["operations"][0]["method"] = "POST"
        self.register_urls()
        httpretty.register_uri(httpretty.POST, "http://localhost/test_http", body='')
        resource = SwaggerClient(u'http://localhost/api-docs').api_test
        resp = resource.testHTTP(body=["a", "b", "c"]).result()
        self.assertEqual(["a", "b", "c"], json.loads(httpretty.last_request().body))
        self.assertEqual(None, resp)

    # ToDo: Wrong body type not being checked as of now...
    @httpretty.activate
    def test_error_on_post_with_wrong_type_body(self):
        pass


if __name__ == '__main__':
    unittest.main()
