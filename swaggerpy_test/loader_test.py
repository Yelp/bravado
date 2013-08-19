#!/usr/bin/env python

#
# Copyright (c) 2013, Digium, Inc.
#

import unittest
import swaggerpy
import swagger_model


class TestProcessor(swagger_model.SwaggerProcessor):
    def process_resource_listing(self, resources, context):
        resources.processed = True


class LoaderTest(unittest.TestCase):
    def test_simple(self):
        uut = swaggerpy.load('test-data/1.1/simple/resources.json',
                             processors=[])
        self.assertEqual('1.1', uut.swaggerVersion)

    def test_processor(self):
        uut = swaggerpy.load('test-data/1.1/simple/resources.json',
                             processors=[TestProcessor()])
        self.assertEqual('1.1', uut.swaggerVersion)
        self.assertTrue(uut.processed)

    def test_missing(self):
        try:
            swaggerpy.load('test-data/1.1/missing/resources.json',
                           processors=[])
            self.fail("Expected load failure b/c of missing file")
        except IOError:
            pass


if __name__ == '__main__':
    unittest.main()
