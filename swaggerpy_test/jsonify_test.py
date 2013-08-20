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

    def test_in(self):
        j = json.loads("""{ "a": 1 }""")
        uut = jsonify(j)
        self.assertTrue('a' in uut)
        self.assertFalse('z' in uut)

    def test_subscript(self):
        j = json.loads("""{ "a": 1, "b": 2, "c": 3 }""")
        uut = jsonify(j)
        self.assertEqual(2, uut['b'])
        self.assertEqual(None, uut['z'])

    def test_items(self):
        j = json.loads("""{ "a": 1, "b": 2, "c": 3 }""")
        uut = jsonify(j)
        self.assertEqual([('a', 1), ('b', 2), ('c', 3)], sorted(uut.items()))

    def test_get_field_names(self):
        j = json.loads("""{ "a": 1, "b": 2, "c": 3 }""")
        uut = jsonify(j)
        self.assertEqual(['a', 'b', 'c'], sorted(uut.get_field_names()))

    def test_values(self):
        j = json.loads("""{ "a": 1, "b": 2, "c": 3 }""")
        uut = jsonify(j)
        self.assertEqual([1, 2, 3], sorted(uut.values()))


if __name__ == '__main__':
    unittest.main()
