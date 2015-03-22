#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
# Copyright (c) 2013, Digium, Inc.
# Copyright (c) 2014, Yelp, Inc.
#

DEFAULT_TIMEOUT_S = 5.0


class HttpFuture(object):
    """A future which inputs HTTP params"""

    def result(self, **kwargs):
        """Blocking call to wait for API response
        """
        raise NotImplementedError(
            u"%s: Method not implemented", self.__class__.__name__)
