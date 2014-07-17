#!/usr/bin/env python

#
# Copyright (c) 2014, Yelp, Inc.
#

"""Swagger client tests to validate resource 'model's

A sample 'model' is listed below in models list.

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

import json
import unittest

import httpretty

from swaggerpy.client import SwaggerClient
from swaggerpy.processors import SwaggerError


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
        api = {
            "path": "/test_http",
            "operations": [operation]
        }
        self.response = {
            "swaggerVersion": "1.2",
            "basePath": "/",
            "apis": [api],
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

    ################################################################
    # Test that swaggerpy correctly creates model
    # classes from swagger model definitions
    # API calls are not triggered here.
    # Scope is limited to model definition in swagger api spec
    ################################################################

    @httpretty.activate
    def test_success_on_model_types_creation(self):
        self.register_urls()
        resource = SwaggerClient(u'http://localhost/api-docs').api_test
        User = resource.models.User
        self.assertEqual({"schools": [], "id": 0L}, User().__dict__)

    @httpretty.activate
    def test_none_for_datetime_on_model_types_creation(self):
        self.models['User']['properties']['date'] = {
            'type': 'string',
            'format': 'date'}
        self.register_urls()
        resource = SwaggerClient(u'http://localhost/api-docs').api_test
        User = resource.models.User
        self.assertEqual({"schools": [], "id": 0L, "date": None},
                         User().__dict__)

    @httpretty.activate
    def test_success_on_model_types_instantiation(self):
        self.register_urls()
        resource = SwaggerClient(u'http://localhost/api-docs').api_test
        User = resource.models.User
        School = resource.models.School
        user = User(id=42, schools=[School(name="a"), School(name="b")])
        user1 = User(schools=[School(name="a"), School(name="b")], id=42)
        self.assertEqual(user1, user)

    # ToDo: DocString generated is not validated as of now

    @httpretty.activate
    def test_error_on_wrong_attr_type_in_model_declaration(self):
        self.response["models"]["School"]["properties"]["name"][
            "type"] = "WRONG_TYPE"
        self.register_urls()
        self.assertRaises(TypeError, SwaggerClient,
                          u'http://localhost/api-docs')

    @httpretty.activate
    def test_error_on_extra_attr_during_model_types_instantiation(self):
        self.register_urls()
        resource = SwaggerClient(u'http://localhost/api-docs').api_test
        User = resource.models.User
        self.assertRaises(AttributeError, User, extra=42)

    @httpretty.activate
    def test_error_on_missing_attr(self):
        def iterate_test(field):
            self.response["models"]["User"].pop(field)
            self.register_urls()
            self.assertRaises(SwaggerError, SwaggerClient,
                              u'http://localhost/api-docs')
        [iterate_test(field) for field in ('id', 'properties')]

    @httpretty.activate
    def test_error_on_model_name_and_id_mismatch(self):
        self.response["models"]["User"]["id"] = "NotUser"
        self.register_urls()
        self.assertRaises(SwaggerError, SwaggerClient,
                          u'http://localhost/api-docs')

    @httpretty.activate
    def test_setattrs_on_client_and_model(self):
        self.register_urls()
        resource = SwaggerClient(u'http://localhost/api-docs').api_test
        models = resource.models
        self.assertTrue(isinstance(models, tuple))
        self.assertNotEqual(None, models.User)
        self.assertEqual(['id'], models.User._required)
        self.assertEqual({
            'schools': 'array:School',
            'id': 'integer:int64'
        }, models.User._swagger_types)
        self.assertNotEqual(None, models.School)
        self.assertEqual(['name'], models.School._required)
        self.assertEqual({'name': 'string'}, models.School._swagger_types)

    @httpretty.activate
    def test_types_of_model_attributes(self):
        self.register_urls()
        resource = SwaggerClient(u'http://localhost/api-docs').api_test
        models = resource.models
        user = models.User()
        school = models.School()
        self.assertTrue(isinstance(user.id, long))
        self.assertTrue(isinstance(user.schools, list))
        self.assertTrue(isinstance(school.name, str))

    ########################################################################
    # Validate that Models specified in the spec have correct Property types
    # API calls are not triggered here. Scope is limited to properties
    # of models defined in swagger api spec
    ########################################################################

    @httpretty.activate
    def test_success_if_ref_but_no_type_in_property(self):
        self.response["models"]["User"]["properties"]["school"] = {
            "$ref": "School"}
        self.register_urls()
        resource = SwaggerClient(u'http://localhost/api-docs').api_test
        self.assertTrue('school' in resource.models.User().__dict__)

    @httpretty.activate
    def test_success_if_type_but_no_ref_in_property(self):
        # Default model. All success tests test this.
        pass

    @httpretty.activate
    def test_error_if_no_ref_no_type_in_property(self):
        # Empty dict assigned which means no ref or no type
        self.response["models"]["User"]["properties"]["school"] = {}
        self.register_urls()
        self.assertRaises(TypeError, SwaggerClient,
                          u'http://localhost/api-docs')

    @httpretty.activate
    def test_error_if_no_complex_in_ref_in_property(self):
        self.response["models"]["User"]["properties"]["school"] = {
            "$ref": "string"}
        self.register_urls()
        self.assertRaises(TypeError, SwaggerClient,
                          u'http://localhost/api-docs')

    @httpretty.activate
    def test_error_if_complex_in_type_in_property(self):
        self.response["models"]["User"]["properties"]["school"] = {
            "type": "School"}
        self.register_urls()
        self.assertRaises(TypeError, SwaggerClient,
                          u'http://localhost/api-docs')

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
        resource = SwaggerClient(u'http://localhost/api-docs').api_test
        resp = resource.testHTTP().result()
        User = resource.models.User
        School = resource.models.School
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
        self.assertRaises(AssertionError, SwaggerClient(
            u'http://localhost/api-docs').api_test.testHTTP().result)

    @httpretty.activate
    def test_error_on_extra_type_instead_of_complex_type(self):
        self.register_urls()
        self.sample_model["extra"] = 42
        httpretty.register_uri(
            httpretty.GET, "http://localhost/test_http",
            body=json.dumps(self.sample_model))
        self.assertRaises(TypeError, SwaggerClient(
            u'http://localhost/api-docs').api_test.testHTTP().result)

    @httpretty.activate
    def test_error_on_wrong_type_instead_of_complex_type(self):
        self.register_urls()
        httpretty.register_uri(
            httpretty.GET, "http://localhost/test_http",
            body='"NOT_COMPLEX_TYPE"')
        self.assertRaises(TypeError, SwaggerClient(
            u'http://localhost/api-docs').api_test.testHTTP().result)

    @httpretty.activate
    def test_error_on_wrong_type_inside_complex_type(self):
        self.register_urls()
        self.sample_model["id"] = "Not Integer"
        httpretty.register_uri(
            httpretty.GET, "http://localhost/test_http",
            body=json.dumps(self.sample_model))
        self.assertRaises(TypeError, SwaggerClient(
            u'http://localhost/api-docs').api_test.testHTTP().result)

    @httpretty.activate
    def test_error_on_wrong_type_inside_nested_complex_type_2(self):
        self.register_urls()
        self.sample_model["schools"][0] = "Not School"
        httpretty.register_uri(
            httpretty.GET, "http://localhost/test_http",
            body=json.dumps(self.sample_model))
        self.assertRaises(TypeError, SwaggerClient(
            u'http://localhost/api-docs').api_test.testHTTP().result)

    @httpretty.activate
    def test_error_on_missing_type_inside_nested_complex_type_1(self):
        self.register_urls()
        self.sample_model["schools"][0] = {}  # Omit 'name'
        httpretty.register_uri(
            httpretty.GET, "http://localhost/test_http",
            body=json.dumps(self.sample_model))
        self.assertRaises(AssertionError, SwaggerClient(
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
        resource = SwaggerClient(u'http://localhost/api-docs').api_test
        school = resource.models.School()
        self.assertRaises(TypeError, resource.testHTTP, test_param=school)

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
        self.response["apis"][0]["operations"][0]["parameters"] = [
            query_parameter]
        self.register_urls()
        resource = SwaggerClient(u'http://localhost/api-docs').api_test
        School = resource.models.School
        # Also test all None items are removed from array list
        user = resource.models.User(id=42, schools=[School(name='s1'), None])
        future = resource.testHTTP(body=user)
        self.assertEqual(json.dumps({'id': 42,
                                     'schools': [{'name': 's1'}]}),
                         future._http_client.request_params['data'])

    @httpretty.activate
    def test_removal_of_none_attributes_from_param_body_model(self):
        query_parameter = {
            "paramType": "body",
            "name": "body",
            "type": "User",
        }
        self.response["apis"][0]["operations"][0]["parameters"] = [
            query_parameter]
        self.response["models"]["User"]["properties"]["school"] = {
            "$ref": "School"}
        self.register_urls()
        resource = SwaggerClient(u'http://localhost/api-docs').api_test
        user = resource.models.User(id=42)
        future = resource.testHTTP(body=user)
        # Removed the 'school': None - key, value pair from dict
        self.assertEqual(json.dumps({'id': 42, 'schools': []}),
                         future._http_client.request_params['data'])

    @httpretty.activate
    def test_error_on_finding_required_attributes_none(self):
        query_parameter = {
            "paramType": "body",
            "name": "body",
            "type": "User",
        }
        self.response["apis"][0]["operations"][0]["parameters"] = [
            query_parameter]
        self.response["models"]["User"]["properties"]["school"] = {
            "$ref": "School"}
        self.response["models"]["User"]["required"] = ["school"]
        self.register_urls()
        resource = SwaggerClient(u'http://localhost/api-docs').api_test
        user = resource.models.User(id=42)
        self.assertRaises(AttributeError, resource.testHTTP, body=user)

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
        self.response["apis"][0]["operations"][0]["type"] = "School"
        self.response["apis"][0]["operations"][0]["parameters"] = [
            query_parameter]
        self.register_urls()
        httpretty.register_uri(
            httpretty.GET, "http://localhost/test_http",
            body=json.dumps(school))
        resource = SwaggerClient(u'http://localhost/api-docs').api_test
        resource.testHTTP(body=school).result()
        self.assertEqual("application/json", httpretty.last_request().headers[
            'content-type'])

    @httpretty.activate
    def test_content_type_not_present_if_only_primitive_type_in_body(self):
        query_parameter = {
            "paramType": "body",
            "name": "body",
            "type": "integer",
        }
        self.response["apis"][0]["operations"][0]["parameters"] = [
            query_parameter]
        self.register_urls()
        httpretty.register_uri(
            httpretty.GET, "http://localhost/test_http",
            body=json.dumps({'id': 1}))
        SwaggerClient(u'http://localhost/api-docs').api_test.testHTTP(
            body=42).result()
        self.assertFalse('content-type' in httpretty.last_request().headers)


if __name__ == '__main__':
    unittest.main()
