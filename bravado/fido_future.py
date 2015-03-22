#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
# Copyright (c) Yelp, Inc.
#

"""Code for checking the response from API. If correct, it proceeds to convert
it into Python class types
"""
import logging

import fido

from bravado.mapping.http_future import HttpFuture, DEFAULT_TIMEOUT_S
from bravado.mapping.operation import unmarshal_response
from bravado.mapping.response import ResponseLike

log = logging.getLogger(__name__)


class FidoResponseAdapter(ResponseLike):
    """Wraps a fido.fido.Response object to provider a uniform interface
    to the response innards.

    :type requests_lib_response: :class:`fido.fido.Response`
    """
    def __init__(self, requests_lib_response):
        self._delegate = requests_lib_response

    @property
    def status_code(self):
        return self._delegate.code

    def json(self, **_):
        return self._delegate.json()


class FidoFuture(HttpFuture):
    """A future which inputs HTTP params"""

    def __init__(self, op, url, request):
        """Kicks API call for Fido client

        :param request: dict containing API request parameters
        """
        self.op = op
        self.url = url
        self.request = request

    def fetch(self):
        self.future = fido.fetch(self.url, **self.request)

    def result(self, timeout=DEFAULT_TIMEOUT_S):
        """Blocking call to wait for API response

        :param timeout: timeout in seconds to wait for response
        :type timeout: integer
        """
        log.debug(u"%s %s(%r)", self.request['method'],
                  self.url, self.request['body'])
        response = self.future.result(timeout=timeout)

        # op is not present during api-docs fetch, return raw response
        if not self.op:
            return response

        return unmarshal_response(FidoResponseAdapter(response),
                                  self.op)
