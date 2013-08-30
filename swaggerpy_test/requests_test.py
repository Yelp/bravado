#!/usr/bin/env python

#
# Copyright (c) 2013, Digium, Inc.
#

import unittest
import swaggerpy.requests


class MyTestCase(unittest.TestCase):
    def setUp(self):
        self.resource_listing = {
            "swaggerVersion": "1.1",
            "basePath": "json:api-docs",
            "apis": [
                {
                    "path": "/api-docs/pet.json",
                    "description": "Test loader when missing a file",
                    "api_declaration": {
                        "swaggerVersion": "1.1",
                        "basePath": "json:api-docs",
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
        self.uut = swaggerpy.requests.client.SwaggerClient(
            resource_listing=self.resource_listing)

    def test_something(self):
        self.uut.apis.pet.listPets()


if __name__ == '__main__':
    unittest.main()
