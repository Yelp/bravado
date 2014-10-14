#!/usr/bin/env python

#
# Copyright (c) 2014, Yelp, Inc.
#

import unittest
from mock import Mock

from swaggerpy.exception import HTTPError


class HTTPErrorTest(unittest.TestCase):
    def setUp(self):
        pass

    def test_request_response_population(self):
        # Give preference to request in parameter
        resp = Mock(**{'request': Mock()})
        req = Mock()
        error = HTTPError(request=req, response=resp)
        self.assertEqual(resp, error.response)
        self.assertEqual(req, error.request)
