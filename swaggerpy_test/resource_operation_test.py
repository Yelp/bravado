#!/usr/bin/env python

"""Swagger client tests to validate resource api operation

ResourceListing > Resource > ResourceApi > "ResourceOperation"
"""

import copy
import httpretty
import json
import unittest

from swaggerpy.client import SwaggerClient
from swaggerpy.processors import SwaggerError


class ResourceOperationTest(unittest.TestCase):
    parameter = {"paramType": "query", "name": "test_param", "type": "string"}
    operation = {"method": "GET", "nickname": "testHTTP", "type": "void", "parameters": [parameter]}
    api = {"path": "/test_http", "operations": [operation]}
    response = {"swaggerVersion": "1.2", "basePath": "/", "apis": [api]}

    def register_urls(self, response):
        httpretty.register_uri(
            httpretty.GET, "http://localhost/api-docs",
            body=json.dumps({"swaggerVersion": "1.2", "apis": [{"path": "/api_test"}]}))
        httpretty.register_uri(
            httpretty.GET, "http://localhost/api-docs/api_test",
            body=json.dumps(response))

    @httpretty.activate
    def test_error_on_missing_attr(self):
        def iterate_test(field):
            response = copy.deepcopy(self.response)
            response["apis"][0]["operations"][0].pop(field)
            self.register_urls(response)
            self.assertRaises(SwaggerError, SwaggerClient, u'http://localhost/api-docs')
        [iterate_test(field) for field in ('method', 'nickname', 'type', 'parameters')]

    # Validate param in operation
    #############################
    # ToDo: Check correctness if $ref is passed (and no type)

    @httpretty.activate
    def test_error_on_missing_attr_in_parameter(self):
        def iterate_test(field):
            response = copy.deepcopy(self.response)
            response["apis"][0]["operations"][0]["parameters"][0].pop(field)
            self.register_urls(response)
            self.assertRaises(SwaggerError, SwaggerClient, u'http://localhost/api-docs')
        [iterate_test(field) for field in ('type', 'paramType', 'name')]

    @httpretty.activate
    def test_error_on_missing_items_param_in_array_parameter(self):
        response = copy.deepcopy(self.response)
        response["apis"][0]["operations"][0]["type"] = "array"
        self.register_urls(response)
        self.assertRaises(SwaggerError, SwaggerClient, u'http://localhost/api-docs')

    @httpretty.activate
    def test_error_on_wrong_attr_type_in_parameter(self):
        response = copy.deepcopy(self.response)
        response["apis"][0]["operations"][0]["parameters"][0]["type"] = "WRONG_TYPE"
        self.register_urls(response)
        self.assertRaises(SwaggerError, SwaggerClient, u'http://localhost/api-docs')

    @httpretty.activate
    def test_error_on_wrong_attr_type_in_array_parameter(self):
        response = copy.deepcopy(self.response)
        response["apis"][0]["operations"][0]["parameters"][0]["type"] = "array"
        response["apis"][0]["operations"][0]["parameters"][0]["items"] = {"type": "WRONG_TYPE"}
        self.register_urls(response)
        self.assertRaises(TypeError, SwaggerClient, u'http://localhost/api-docs')

    @httpretty.activate
    def test_error_on_missing_param_in_error_response(self):
        msg = {"code": 400, "message": "some message"}

        def iterate_test(field):
            response = copy.deepcopy(self.response)
            response["apis"][0]["operations"][0]["responseMessages"] = [msg]
            response["apis"][0]["operations"][0]["responseMessages"][0].pop(field)
            self.register_urls(response)
            self.assertRaises(SwaggerError, SwaggerClient, u'http://localhost/api-docs')
        [iterate_test(field) for field in ('code', 'message')]

    # Validate paramType of parameters - path, query, body
    ######################################################

    @httpretty.activate
    def test_success_on_GET_with_path_and_query_params(self):
        query_parameter = self.parameter
        path_parameter = {"paramType": "path", "name": "param_id", "type": "string"}
        response = copy.deepcopy(self.response)
        response["apis"][0]["path"] = "/params/{param_id}/test_http"
        response["apis"][0]["operations"][0]["parameters"] = [query_parameter, path_parameter]
        self.register_urls(response)
        httpretty.register_uri(
            httpretty.GET, "http://localhost/params/42/test_http?test_param=foo",
            body='')
        resource = SwaggerClient(u'http://localhost/api-docs').api_test
        resp = resource.testHTTP(test_param="foo", param_id="42")
        self.assertEqual(200, resp.status_code)

    @httpretty.activate
    def test_success_on_GET_with_array_in_path_and_query_params(self):
        query_parameter = {"paramType": "query", "name": "test_params", "type": "array", "items": {"type": "string"}}
        path_parameter = {"paramType": "path", "name": "param_ids", "type": "array", "items": {"type": "integer"}}
        response = copy.deepcopy(self.response)
        response["apis"][0]["path"] = "/params/{param_ids}/test_http"
        response["apis"][0]["operations"][0]["parameters"] = [query_parameter, path_parameter]
        self.register_urls(response)
        httpretty.register_uri(
            httpretty.GET, "http://localhost/params/40,41,42/test_http?test_param=foo,bar",
            body='')
        resource = SwaggerClient(u'http://localhost/api-docs').api_test
        resp = resource.testHTTP(test_params=["foo", "bar"], param_ids=[40, 41, 42])
        self.assertEqual(200, resp.status_code)

    """
    # ToDo: Wrong param type not being checked as of now... Commented test is expected to fail
    @httpretty.activate
    def test_error_on_GET_with_wrong_type_param(self):
        query_parameter = {"paramType": "query", "name": "test_param", "type": "integer"}
        response = copy.deepcopy(self.response)
        response["apis"][0]["operations"][0]["parameters"] = [query_parameter]
        self.register_urls(response)
        resource = SwaggerClient(u'http://localhost/api-docs').api_test
        self.assertRaises(TypeError, resource.testHTTP, test_param="NOT_INTEGER")
    """

    @httpretty.activate
    def test_success_on_POST_with_path_query_and_body_params(self):
        query_parameter = self.parameter
        path_parameter = {"paramType": "path", "name": "param_id", "type": "string"}
        body_parameter = {"paramType": "body", "name": "body", "type": "string"}
        response = copy.deepcopy(self.response)
        response["apis"][0]["path"] = "/params/{param_id}/test_http"
        response["apis"][0]["operations"][0]["method"] = "POST"
        response["apis"][0]["operations"][0]["parameters"] = [query_parameter,
                                                              path_parameter,
                                                              body_parameter]
        self.register_urls(response)
        httpretty.register_uri(
            httpretty.POST, "http://localhost/params/42/test_http?test_param=foo",
            body='')
        resource = SwaggerClient(u'http://localhost/api-docs').api_test
        resp = resource.testHTTP(test_param="foo", param_id="42", body="some_test")
        self.assertEqual('application/json', httpretty.last_request().headers['content-type'])
        self.assertEqual('some_test', httpretty.last_request().body)
        self.assertEqual(200, resp.status_code)

    @httpretty.activate
    def test_success_on_POST_with_array_in_body_params(self):
        body_parameter = {"paramType": "body", "name": "body", "type": "array", "items": {"type": "string"}}
        response = copy.deepcopy(self.response)
        response["apis"][0]["operations"][0]["parameters"] = [body_parameter]
        response["apis"][0]["operations"][0]["method"] = "POST"
        self.register_urls(response)
        httpretty.register_uri(httpretty.POST, "http://localhost/test_http", body='')
        resource = SwaggerClient(u'http://localhost/api-docs').api_test
        resp = resource.testHTTP(body=["a", "b", "c"])
        self.assertEqual(["a", "b", "c"], json.loads(httpretty.last_request().body))
        self.assertEqual(200, resp.status_code)

    # ToDo: Wrong body type not being checked as of now...
    @httpretty.activate
    def test_error_on_POST_with_wrong_type_body(self):
        pass

    def setUp(self):
        pass


if __name__ == '__main__':
    unittest.main()
