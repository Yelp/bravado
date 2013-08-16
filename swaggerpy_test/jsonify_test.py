#!/usr/bin/env python

#
# Copyright (c) 2013, Digium, Inc.
#

import json
import unittest
from swaggerpy.jsonify import jsonify


class JsonifyTest(unittest.TestCase):
    def test_object(self):
        j = json.loads("""{ "a": 1 }""")
        uut = jsonify(j)
        self.assertEqual(1, uut.a)

    def test_array(self):
        j = json.loads("""[ { "a": 1 }, 2, "c" ]""")
        uut = jsonify(j)
        self.assertEqual(1, uut[0].a)
        self.assertEqual(2, uut[1])
        self.assertEqual("c", uut[2])


if __name__ == '__main__':
    unittest.main()
