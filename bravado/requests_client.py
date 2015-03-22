#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
# Copyright (c) 2013, Digium, Inc.
# Copyright (c) 2014, Yelp, Inc.
#

import logging

import requests
import requests.auth

from bravado.mapping.http_client import (Authenticator,
                                         ApiKeyAuthenticator,
                                         HttpClient)
from bravado.requests_future import RequestsFuture

log = logging.getLogger(__name__)


class BasicAuthenticator(Authenticator):
    """HTTP Basic authenticator.

    :param host: Host to authenticate for.
    :param username: Username.
    :param password: Password
    """

    def __init__(self, host, username, password):
        super(BasicAuthenticator, self).__init__(host)
        self.auth = requests.auth.HTTPBasicAuth(username, password)

    def apply(self, request):
        request.auth = self.auth

        return request


class RequestsClient(HttpClient):
    """Synchronous HTTP client implementation.
    """

    def __init__(self):
        self.session = requests.Session()
        self.authenticator = None

    def request(self, request_params, op=None):
        """
        :param request_params: complete request data.
        :type request_params: dict
        :return: request
        :rtype: requests.Request
        """
        return RequestsFuture(
            op,
            self.session,
            self.authenticated_request(request_params))

    def set_basic_auth(self, host, username, password):
        self.authenticator = BasicAuthenticator(
            host=host, username=username, password=password)

    def set_api_key(self, host, api_key, param_name=u'api_key'):
        self.authenticator = ApiKeyAuthenticator(
            host=host, api_key=api_key, param_name=param_name)

    def authenticated_request(self, request_params):
        return self.apply_authentication(requests.Request(**request_params))

    def apply_authentication(self, request):
        if self.authenticator and self.authenticator.matches(request.url):
            return self.authenticator.apply(request)

        return request
