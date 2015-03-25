#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
# Copyright (c) 2013, Digium, Inc.
# Copyright (c) 2014, Yelp, Inc.
#

"""HTTP client abstractions.
"""

APP_FORM = 'application/x-www-form-urlencoded'
APP_JSON = 'application/json'
MULT_FORM = 'multipart/form-data'


class HttpClient(object):
    """Interface for a minimal HTTP client.
    """

    def request(self, request_params, response_callback=None):
        """
        :param request_params: complete request data.
        :type request_params: dict
        :param response_callback: Function to be called on response
        :type response_callback: method

        :returns: HTTP Future object
        :rtype: :class: `bravado.mapping.http_future.HttpFuture`
        """
        raise NotImplementedError(
            u"%s: Method not implemented", self.__class__.__name__)

    def __repr__(self):
        return "{0}()".format(type(self))
