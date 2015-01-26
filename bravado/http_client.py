#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
# Copyright (c) 2013, Digium, Inc.
# Copyright (c) 2014, Yelp, Inc.
#

"""HTTP client abstractions.
"""
import logging
import urlparse

import requests
import requests.auth

log = logging.getLogger(__name__)
APP_FORM = 'application/x-www-form-urlencoded'
APP_JSON = 'application/json'
MULT_FORM = 'multipart/form-data'


class HttpClient(object):
    """Interface for a minimal HTTP client.
    """

    def request(self, method, url, params=None, data=None):
        """Issue an HTTP request.

        :param method: HTTP method (GET, POST, DELETE, etc.)
        :type  method: str
        :param url: URL to request
        :type  url: str
        :param params: Query parameters (?key=value)
        :type  params: dict
        :param data: Request body
        :type  data: Dictionary, bytes, or file-like object
        :return: Implementation specific response object
        """
        raise NotImplementedError(
            u"%s: Method not implemented", self.__class__.__name__)

    def set_basic_auth(self, host, username, password):
        """Configures client to use HTTP Basic authentication.

        :param host: Hostname to limit authentication to.
        :param username: Username
        :param password: Password
        """
        raise NotImplementedError(
            u"%s: Method not implemented", self.__class__.__name__)

    def set_api_key(self, host, api_key, param_name=u'api_key'):
        """Configures client to use api_key authentication.

        The api_key is added to every query parameter sent.

        :param host: Hostname to limit authentication to.
        :param api_key: Value for api_key.
        :param param_name: Parameter name to use in query string.
        """
        raise NotImplementedError(
            u"%s: Method not implemented", self.__class__.__name__)

    def start_request(self, request_params):
        """
        :param request_params: Complete request data.
        :type request_params: dict

        :returns: The client's request object
        """
        raise NotImplementedError(
            u"%s: Method not implemented", self.__class__.__name__)

    def __repr__(self):
        return "{0}()".format(type(self))


class Authenticator(object):
    """Authenticates requests.

    :param host: Host to authenticate for.
    """

    def __init__(self, host):
        self.host = host

    def __repr__(self):
        return u"%s(%s)" % (self.__class__.__name__, self.host)

    def matches(self, url):
        """Returns true if this authenticator applies to the given url.

        :param url: URL to check.
        :return: True if matches host, port and scheme, False otherwise.
        """
        split = urlparse.urlsplit(url)
        return self.host == split.hostname

    def apply(self, request):
        """Apply authentication to a request.

        :param request: Request to add authentication information to.
        """
        raise NotImplementedError(u"%s: Method not implemented",
                                  self.__class__.__name__)


# noinspection PyDocstring
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


# noinspection PyDocstring
class ApiKeyAuthenticator(Authenticator):
    """?api_key authenticator.

    This authenticator adds a query parameter to specify an API key.

    :param host: Host to authenticate for.
    :param api_key: API key.
    :param param_name: Query parameter specifying the API key.
    """

    def __init__(self, host, api_key, param_name=u'api_key'):
        super(ApiKeyAuthenticator, self).__init__(host)
        self.param_name = param_name
        self.api_key = api_key

    def apply(self, request):
        request.params[self.param_name] = self.api_key
        return request


class SynchronousHttpClient(HttpClient):
    """Synchronous HTTP client implementation.
    """

    def __init__(self):
        self.session = requests.Session()
        self.authenticator = None

    def start_request(self, request_params):
        """
        :return: request
        :rtype: requests.Request
        """
        return SynchronousEventual(
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


class SynchronousEventual(object):
    """An adapter which supports the :class:`crochet.EventualResult` interface
    for the :class:`SynchronousHttpClient` class.
    """

    def __init__(self, session, request):
        self.session = session
        self.request = request

    def wait(self, timeout=None):
        """Perform the request.

        :param timeout: timeout for the request, in seconds
        """
        request = self.request
        log.debug(u"%s %s(%r)", request.method, request.url, request.params)
        return self.session.send(
            self.session.prepare_request(request),
            timeout=timeout)

    def cancel(self):
        pass
