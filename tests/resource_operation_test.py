#!/usr/bin/env python
# -*- coding: utf-8 -*-

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

import datetime
from swaggerpy.compat import json
import unittest
import urlparse

import httpretty
from dateutil.tz import tzutc

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
            self.assertRaises(SwaggerError, SwaggerClient.from_url,
                              u'http://localhost/api-docs')
        [iterate_test(field) for field in ('method', 'nickname', 'type',
                                           'parameters')]

    #############################
    # Validate param in operation
    #############################
    # ToDo: Check correctness if $ref is passed (and no type)

    @httpretty.activate
    def test_error_on_missing_attr_in_parameter(self):
        def iterate_test(field):
            self.response["apis"][0]["operations"][0]["parameters"][0].pop(
                field)
            self.register_urls()
            self.assertRaises(SwaggerError, SwaggerClient.from_url,
                              u'http://localhost/api-docs')
        [iterate_test(field) for field in ('type', 'paramType', 'name')]

    @httpretty.activate
    def test_error_on_missing_items_param_in_array_parameter(self):
        self.response["apis"][0]["operations"][0]["type"] = "array"
        self.register_urls()
        self.assertRaises(SwaggerError, SwaggerClient.from_url,
                          u'http://localhost/api-docs')

    @httpretty.activate
    def test_error_on_having_body_and_form_both_in_parameter(self):
        params = self.response["apis"][0]["operations"][0]["parameters"]
        params.append({"paramType": "body", "type": "string", "name": "a"})
        params.append({"paramType": "form", "type": "string", "name": "b"})
        self.register_urls()
        self.assertRaises(AttributeError, SwaggerClient.from_url,
                          u'http://localhost/api-docs')

    @httpretty.activate
    def test_error_on_wrong_attr_type_in_parameter(self):
        parameters = self.response["apis"][0]["operations"][0]["parameters"]
        parameters[0]["type"] = "WRONG_TYPE"
        self.register_urls()
        self.assertRaises(SwaggerError, SwaggerClient.from_url,
                          u'http://localhost/api-docs')

    @httpretty.activate
    def test_error_on_wrong_attr_type_in_array_parameter(self):
        parameters = self.response["apis"][0]["operations"][0]["parameters"]
        parameters[0]["type"] = "array"
        parameters[0]["items"] = {"type": "WRONG_TYPE"}
        self.register_urls()
        self.assertRaises(SwaggerError, SwaggerClient.from_url,
                          u'http://localhost/api-docs')

    @httpretty.activate
    def test_error_on_missing_param_in_error_response(self):
        msg = {"code": 400, "message": "some message"}

        def iterate_test(field):
            operations = self.response["apis"][0]["operations"]
            operations[0]["responseMessages"] = [msg]
            operations[0]["responseMessages"][0].pop(field)
            self.register_urls()
            self.assertRaises(SwaggerError, SwaggerClient.from_url,
                              u'http://localhost/api-docs')
        [iterate_test(field) for field in ('code', 'message')]

    ######################################################
    # Validate paramType of parameters - path, query, body
    ######################################################

    # Validate form parameters
    @httpretty.activate
    def test_success_on_post_with_form_params(self):
        form_parameter_1 = {
            "paramType": "form",
            "name": "param_id",
            "type": "integer"
        }
        form_parameter_2 = {
            "paramType": "form",
            "name": "param_name",
            "type": "string"
        }
        self.response["apis"][0]["operations"][0]["method"] = "POST"
        self.response["apis"][0]["operations"][0]["parameters"] = [
            form_parameter_1, form_parameter_2]
        self.register_urls()
        httpretty.register_uri(
            httpretty.POST, "http://localhost/test_http?", body='')
        resource = SwaggerClient.from_url(
            u'http://localhost/api-docs').api_test
        resource.testHTTP(param_id=42, param_name='str').result()
        self.assertEqual('application/x-www-form-urlencoded',
                         httpretty.last_request().headers['content-type'])
        self.assertEqual({'param_name': ['str'], 'param_id': ['42']},
                         urlparse.parse_qs(httpretty.last_request().body))

    @httpretty.activate
    def test_success_on_post_with_form_params_with_files(self):
        form_parameter_1 = {
            "paramType": "form",
            "name": "param_id",
            "type": "integer"
        }
        form_parameter_2 = {
            "paramType": "form",
            "name": "file_name",
            "type": "File"
        }
        self.response["apis"][0]["operations"][0]["method"] = "POST"
        self.response["apis"][0]["operations"][0]["parameters"] = [
            form_parameter_1, form_parameter_2]
        self.register_urls()
        httpretty.register_uri(
            httpretty.POST, "http://localhost/test_http?", body='')
        resource = SwaggerClient.from_url(
            u'http://localhost/api-docs').api_test
        with open("test-data/1.2/simple/simple.json", "rb") as f:
            resource.testHTTP(param_id=42, file_name=f).result()
            content_type = httpretty.last_request().headers['content-type']

            self.assertTrue(content_type.startswith('multipart/form-data'))
            self.assertTrue("42" in httpretty.last_request().body)
            # instead of asserting the contents, just assert filename is there
            self.assertTrue("simple.json" in httpretty.last_request().body)

    @httpretty.activate
    def test_success_on_get_with_path_and_query_params(self):
        query_parameter = self.parameter
        path_parameter = {
            "paramType": "path",
            "name": "param_id",
            "type": "string"
        }
        self.response["apis"][0]["path"] = "/params/{param_id}/test_http"
        self.response["apis"][0]["operations"][0]["parameters"] = [
            query_parameter, path_parameter]
        self.register_urls()
        httpretty.register_uri(
            httpretty.GET,
            "http://localhost/params/42/test_http?test_param=foo",
            body='')
        resource = SwaggerClient.from_url(
            u'http://localhost/api-docs').api_test
        resp = resource.testHTTP(test_param="foo", param_id="42").result()
        self.assertEqual(None, resp)

    @httpretty.activate
    def test_success_on_passing_default_value_if_param_not_passed(self):
        self.parameter['defaultValue'] = 'testString'
        self.register_urls()
        httpretty.register_uri(httpretty.GET,
                               "http://localhost/test_http?", body='')
        resource = SwaggerClient.from_url(
            u'http://localhost/api-docs').api_test
        resource.testHTTP().result()
        self.assertEqual(['testString'],
                         httpretty.last_request().querystring['test_param'])

    @httpretty.activate
    def test_success_on_get_with_array_in_path_and_query_params(self):
        query_parameter = {
            "paramType": "query",
            "name": "test_params",
            "type": "string"}
        path_parameter = {
            "paramType": "path",
            "name": "param_ids",
            "type": "array",
            "items": {
                "type": "integer"}}
        self.response["apis"][0]["path"] = "/params/{param_ids}/test_http"
        self.response["apis"][0]["operations"][0]["parameters"] = [
            query_parameter, path_parameter]
        self.register_urls()
        httpretty.register_uri(
            httpretty.GET,
            "http://localhost/params/40,41,42/test_http?", body='')
        resource = SwaggerClient.from_url(
            u'http://localhost/api-docs').api_test
        resp = resource.testHTTP(test_params=["foo", "bar"],
                                 param_ids=[40, 41, 42]).result()
        self.assertEqual(["foo", "bar"],
                         httpretty.last_request().querystring['test_params'])
        self.assertEqual(None, resp)

    @httpretty.activate
    def test_error_on_get_with_wrong_type_in_query(self):
        query_parameter = {
            "paramType": "query",
            "name": "test_param",
            "type": "integer"
        }
        self.response["apis"][0]["operations"][0]["parameters"] = [
            query_parameter]
        self.register_urls()
        resource = SwaggerClient.from_url(
            u'http://localhost/api-docs').api_test
        self.assertRaises(TypeError, resource.testHTTP,
                          test_param="NOT_INTEGER")

    @httpretty.activate
    def test_error_on_get_with_array_type_in_query(self):
        query_parameter = {
            "paramType": "query",
            "name": "test_param",
            "type": "array",
            "items": {"type": "string"}
        }
        self.response["apis"][0]["operations"][0]["parameters"] = [
            query_parameter]
        self.register_urls()
        resource = SwaggerClient.from_url(
            u'http://localhost/api-docs').api_test
        self.assertRaises(TypeError, resource.testHTTP, test_param=["A", "B"])

    @httpretty.activate
    def test_no_error_on_not_passing_non_required_param_in_query(self):
        self.register_urls()
        resource = SwaggerClient.from_url(
            u'http://localhost/api-docs').api_test
        # No error should be raised on not passing test_param (not required)
        resource.testHTTP()

    @httpretty.activate
    def test_error_on_get_with_wrong_array_item_type_in_query(self):
        query_parameter = {
            "paramType": "query",
            "name": "test_param",
            "type": "array",
            "items": {"type": "integer"}
        }
        self.response["apis"][0]["operations"][0]["parameters"] = [
            query_parameter]
        self.register_urls()
        resource = SwaggerClient.from_url(
            u'http://localhost/api-docs').api_test
        self.assertRaises(TypeError, resource.testHTTP,
                          test_param=["NOT_INTEGER"])

    @httpretty.activate
    def test_success_on_passing_datetime_in_param(self):
        query_parameter = {
            "paramType": "query",
            "name": "test_param",
            "type": "string",
            "format": "date-time"
        }
        self.response["apis"][0]["operations"][0]["parameters"] = [
            query_parameter]
        httpretty.register_uri(
            httpretty.GET, "http://localhost/test_http", body='')
        self.register_urls()
        resource = SwaggerClient.from_url(
            u'http://localhost/api-docs').api_test
        some_datetime = datetime.datetime(
            2014, 6, 10, 23, 49, 54, 728000, tzinfo=tzutc())
        resource.testHTTP(test_param=some_datetime).result()
        self.assertEqual(['2014-06-10 23:49:54.728000 00:00'],
                         httpretty.last_request().querystring['test_param'])

    @httpretty.activate
    def test_success_on_passing_date_in_param(self):
        query_parameter = {
            "paramType": "query",
            "name": "test_param",
            "type": "string",
            "format": "date"
        }
        self.response["apis"][0]["operations"][0]["parameters"] = [
            query_parameter]
        httpretty.register_uri(
            httpretty.GET, "http://localhost/test_http", body='')
        self.register_urls()
        resource = SwaggerClient.from_url(
            u'http://localhost/api-docs').api_test
        some_date = datetime.date(2014, 6, 10)
        resource.testHTTP(test_param=some_date).result()
        self.assertEqual(['2014-06-10'],
                         httpretty.last_request().querystring['test_param'])

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
        operations = self.response["apis"][0]["operations"]
        operations[0]["method"] = "POST"
        operations[0]["parameters"] = [query_parameter,
                                       path_parameter,
                                       body_parameter]
        self.register_urls()
        httpretty.register_uri(
            httpretty.POST,
            "http://localhost/params/42/test_http?test_param=foo", body='')
        resource = SwaggerClient.from_url(
            u'http://localhost/api-docs').api_test
        resp = resource.testHTTP(test_param="foo", param_id="42",
                                 body="some_test").result()
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
        operations = self.response["apis"][0]["operations"]
        operations[0]["parameters"] = [body_parameter]
        operations[0]["method"] = "POST"
        self.register_urls()
        httpretty.register_uri(httpretty.POST, "http://localhost/test_http",
                               body='')
        resource = SwaggerClient.from_url(
            u'http://localhost/api-docs').api_test
        resp = resource.testHTTP(body=["a", "b", "c"]).result()
        self.assertEqual(["a", "b", "c"],
                         json.loads(httpretty.last_request().body))
        self.assertEqual(None, resp)

    # ToDo: Wrong body type not being checked as of now...
    @httpretty.activate
    def test_error_on_post_with_wrong_type_body(self):
        pass


if __name__ == '__main__':
    unittest.main()
