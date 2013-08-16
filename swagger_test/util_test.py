#!/usr/bin/env python

#
# Copyright (c) 2013, Digium, Inc.
#

import unittest

class UtilTest(unittest.TestCase):
    def test_fail(self):
        self.assertEqual(True, False)

if __name__ == '__main__':
    unittest.main()
