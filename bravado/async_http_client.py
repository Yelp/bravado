#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
# Copyright (c) 2014, Yelp, Inc.
#

"""Asynchronous HTTP client abstractions.
"""

import logging

import fido
from yelp_uri import urllib_utf8

from bravado import http_client
from bravado.multipart_response import create_multipart_content
from bravado.mapping.param import stringify_body as param_stringify_body

log = logging.getLogger(__name__)


class AsynchronousHttpClient(http_client.HttpClient):
    """Asynchronous HTTP client implementation.
    """

    def start_request(self, request_params):
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

        # crochet only supports bytes for the url
        if isinstance(url, unicode):
            url = url.encode('utf-8')

        return fido.fetch(url, **request_params)


def stringify_body(request_params):
    """Wraps the data using twisted FileBodyProducer
    """
    data = None
    headers = request_params.get('headers', {})
    if 'files' in request_params:
        data = create_multipart_content(request_params, headers)
    elif headers.get('content-type') == http_client.APP_FORM:
        data = urllib_utf8.urlencode(request_params.get('data', {}))
    else:
        # TODO: same method 'stringify_body' exists with different args - fix!
        data = param_stringify_body(request_params.get('data', ''))
    return data
