#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
# Copyright (c) 2015, Yelp, Inc.
#
import logging

from bravado.mapping.http_future import HttpFuture, DEFAULT_TIMEOUT_S
from bravado.mapping.operation import unmarshal_response
from bravado.mapping.response import ResponseLike

log = logging.getLogger(__name__)


def add_response_detail_to_errors(e):
    """Specific to requests errors. Error detail is not
    directly visible in `raise_for_status` trace, instead it is
    located under `e.response.text`
    """
    if hasattr(e, 'response') and hasattr(e.response, 'text'):
        # e.args is a tuple, change to list for modifications
        args = list(e.args)
        args[0] += (' : ' + e.response.text)
        e.args = tuple(args)
    raise e


class RequestsResponseAdapter(ResponseLike):
    """Wraps a requests.models.Response object to provide a uniform interface
    to the response innards.
    """

    def __init__(self, requests_lib_response):
        """
        :type requests_lib_response: :class:`requests.models.Response`
        """
        self._delegate = requests_lib_response

    @property
    def status_code(self):
        return self._delegate.status_code

    def json(self, **kwargs):
        return self._delegate.json(**kwargs)


class RequestsFuture(HttpFuture):
    """A future which inputs HTTP params"""

    def __init__(self, op, session, request):
        """Kicks API call for Requests client

        :param request: dict containing API request parameters
        """
        self.op = op
        self.session = session
        self.request = request

    def check_for_exceptions(self, response):
        try:
            response.raise_for_status()
        except Exception as e:
            add_response_detail_to_errors(e)

    def result(self, timeout=DEFAULT_TIMEOUT_S):
        """Blocking call to wait for API response

        :param timeout: timeout in seconds to wait for response
        :type timeout: integer
        """
        request = self.request
        log.debug(u"%s %s(%r)", request.method, request.url, request.params)
        response = self.session.send(
            self.session.prepare_request(request),
            timeout=timeout)

        self.check_for_exceptions(response)

        # op is not present during api-docs fetch, return raw response
        if not self.op:
            return response

        return unmarshal_response(RequestsResponseAdapter(response),
                                  self.op)
