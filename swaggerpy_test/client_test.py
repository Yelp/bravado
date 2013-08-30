#!/usr/bin/env python

#
# Copyright (c) 2013, Digium, Inc.
#

import requests
from swaggerpy.client import SwaggerClient
import unittest


class ClientTest(unittest.TestCase):
    def test_something(self):
        try:
            self.uut.apis.pet.listPets()
            self.fail("Should have gotten a connection failure")
        except requests.ConnectionError:
            pass

    def setUp(self):
        self.resource_listing = {
            "swaggerVersion": "1.1",
            "basePath": "http://localhost:8000/swagger-test",
            "apis": [
                {
                    "path": "/api-docs/pet.json",
                    "description": "Test loader when missing a file",
                    "api_declaration": {
                        "swaggerVersion": "1.1",
                        "basePath": "http://localhost:8000/swagger-test",
                        "resourcePath": "/pet.json",
                        "apis": [
                            {
                                "path": "/pet",
                                "operations": [
                                    {
                                        "httpMethod": "GET",
                                        "nickname": "listPets"
                                    }
                                ]
                            }
                        ],
                        "models": {}
                    }
                }
            ]
        }
        self.uut = SwaggerClient(
            resource_listing=self.resource_listing)


if __name__ == '__main__':
    unittest.main()
