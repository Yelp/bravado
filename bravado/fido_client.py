#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
# Copyright (c) 2015, Yelp, Inc.
#

import logging

from yelp_uri import urllib_utf8

from bravado.fido_future import FidoFuture
from bravado.mapping.http_client import APP_FORM, HttpClient
from bravado.multipart_response import create_multipart_content
from bravado.mapping.param import stringify_body as param_stringify_body

log = logging.getLogger(__name__)


class FidoClient(HttpClient):
    """Fido HTTP client implementation.
    """

    def request(self, request_params, op=None):
        """Sets up the request params as per Twisted Agent needs.
        Sets up crochet and triggers the API request in background

        :param request_params: request parameters for API call
        :type request_params: dict

        :return: crochet EventualResult
        """
        url = '%s?%s' % (request_params['url'], urllib_utf8.urlencode(
            request_params.get('params', []), True))

        request_params = {
            'method': str(request_params.get('method', 'GET')),
            'body': stringify_body(request_params),
            'headers': request_params.get('headers', {}),
        }

        fido_future = FidoFuture(op, url, request_params)
        fido_future.fetch()
        return fido_future


def stringify_body(request_params):
    """Wraps the data using twisted FileBodyProducer
    """
    headers = request_params.get('headers', {})
    if 'files' in request_params:
        return create_multipart_content(request_params, headers)
    if headers.get('content-type') == APP_FORM:
        return urllib_utf8.urlencode(request_params.get('data', {}))

    # TODO: same method 'stringify_body' exists with different args - fix!
    return param_stringify_body(request_params.get('data', ''))
