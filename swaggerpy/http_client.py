#!/usr/bin/env python

#
# Copyright (c) 2013, Digium, Inc.
#

"""HTTP client abstractions.
"""

import json
import logging
import urlparse
from cStringIO import StringIO
import urllib

import crochet
import requests
import requests.auth
import twisted.internet.error
import twisted.web.client
import websocket
from twisted.internet import reactor
from twisted.internet.defer import Deferred
from twisted.internet.protocol import Protocol
from twisted.web.client import Agent
from twisted.web.client import FileBodyProducer
from twisted.web.client import WebClientContextFactory
from twisted.web.http_headers import Headers


log = logging.getLogger(__name__)


class HttpClient(object):
    """Interface for a minimal HTTP client.
    """

    def close(self):
        """Close this client resource.
        """
        raise NotImplementedError(
            u"%s: Method not implemented", self.__class__.__name__)

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

    def ws_connect(self, url, params=None):
        """Create a WebSocket connection.

        :param url: WebSocket URL.
        :type  url: str
        :param params: Query parameters (?key=value)
        :type  params: dict
        :return: Implmentation specific WebSocket connection object
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

    def setup(self, request_params):
        """Store the request params for calling later.

        :param request_params: Complete request data.
        :type request_params: dict
        """
        raise NotImplementedError(
            u"%s: Method not implemented", self.__class__.__name__)

    def wait(self, timeout):
        """Similar to 'request', Calls the API with request_params until timeout.

        :param timeout: time in seconds to wait for response.
        :type timeout: float
        :return: Implementation specific response
        """
        raise NotImplementedError(
            u"%s: Method not implemented", self.__class__.__name__)


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


class AsynchronousHttpClient(HttpClient):
    """Asynchronous HTTP client implementation.
    """

    def setup(self, request_params):
        self.request_params = request_params
        data = self.request_params.pop('data', None)
        params = self.request_params.pop('params')
        url = self.request_params.pop('url', '')
        if self.request_params.get('headers'):
            self.request_params['headers'] = Headers(self.request_params['headers'])
        """
            if self.request_params['headers'].get('content-type') == 'application/json':
                if data and not isinstance(data, (str, unicode)):
                    data = json.dumps(data)
        """
        if data:
            self.request_params['bodyProducer'] = FileBodyProducer(StringIO(data))
        self.request_params['method'] = str(self.request_params['method'])
        self.request_params['uri'] = str(url + "?" + urllib.urlencode(params))
        crochet.setup()
        self.eventual = self.fetch_http_inner()

    def wait(self, timeout):
        """Requests based implemention with timeout

        :param timeout: time in seconds to wait for response
        :return: Requests response
        :rtype:  requests.Response
        """
        log.info(u"%s %s(%r)", self.request_params.get('method'),
                 self.request_params.get('url'),
                 self.request_params.get('params'))
        return self.eventual.wait(timeout)

    @crochet.run_in_reactor
    def fetch_http_inner(self):

        finished = Deferred()

        agent = Agent(
            reactor,
            connectTimeout=None,
            contextFactory=WebClientContextFactory())

        deferred = agent.request(**self.request_params)

        def response_callback(response):
            response.deliverBody(_HTTPBodyFetcher(self.request_params, response, finished))
        deferred.addCallback(response_callback)

        def response_errback(reason):
            finished.errback(reason)
        deferred.addErrback(response_errback)

        return finished


class HTTPResponse(object):

    def __init__(self, request, code, headers, body):
        self.request = request
        self.headers = dict(headers.getAllRawHeaders())
        self.code = code
        self.text = body

    def json(self):
        return json.loads(self.text)

    def raise_for_status(self):
        pass


class _HTTPBodyFetcher(Protocol):

    def __init__(self, request, response, finished):
        self.buffer = StringIO()
        self.request = request
        self.response = response
        self.finished = finished

    def dataReceived(self, data):
        self.buffer.write(data)

    def connectionLost(self, reason):
        if reason.check(twisted.web.client.ResponseDone) or reason.check(twisted.web.http.PotentialDataLoss):
            self.finished.callback(
                HTTPResponse(
                    request=self.request,
                    code=self.response.code,
                    headers=self.response.headers,
                    body=self.buffer.getvalue()))
        else:
            self.finished.errback(reason)


# noinspection PyDocstring
class SynchronousHttpClient(HttpClient):
    """Synchronous HTTP client implementation.
    """

    def __init__(self):
        self.session = requests.Session()
        self.authenticator = None
        self.websockets = set()

    def close(self):
        self.session.close()
        # There's no WebSocket factory to close; close connections individually

    def setup(self, request_params):
        self.request_params = request_params
        if self.request_params.get('headers'):
            if self.request_params['headers'].get('content-type') == 'application/json':
                data = self.request_params['data']
                if not isinstance(data, (str, unicode)):
                    self.request_params['data'] = json.dumps(data)

    def set_basic_auth(self, host, username, password):
        self.authenticator = BasicAuthenticator(
            host=host, username=username, password=password)

    def set_api_key(self, host, api_key, param_name=u'api_key'):
        self.authenticator = ApiKeyAuthenticator(
            host=host, api_key=api_key, param_name=param_name)

    def wait(self, timeout):
        """Requests based implemention with timeout
        No support of Websockets.

        :param timeout: time in seconds to wait for response
        :return: Requests response
        :rtype:  requests.Response
        """
        log.info(u"%s %s(%r)", self.request_params.get('method'),
                 self.request_params.get('url'),
                 self.request_params.get('params'))
        req = requests.Request(**self.request_params)
        self.apply_authentication(req)
        return self.session.send(self.session.prepare_request(req), timeout=timeout)

    def request(self, method, url, params=None, data=None, headers=None):
        """Requests based implementation.

        :return: Requests response
        :rtype:  requests.Response
        """
        if headers and headers.get('content-type') == 'application/json':
            data = data if isinstance(data, (str, unicode)) else json.dumps(data)
        kwargs = {}
        for i in ('method', 'url', 'params', 'data', 'headers'):
            kwargs[i] = locals()[i]
        req = requests.Request(**kwargs)
        self.apply_authentication(req)
        return self.session.send(self.session.prepare_request(req))

    def ws_connect(self, url, params=None):
        """Websocket-client based implementation.

        :return: WebSocket connection
        :rtype:  websocket.WebSocket
        """
        # Build a prototype request and apply authentication to it
        proto_req = requests.Request(u'GET', url, params=params)
        self.apply_authentication(proto_req)
        # Prepare the request, so params will be put on the url,
        # and authenticators can manipulate headers
        preped_req = proto_req.prepare()
        # Pull the Authorization header, if needed
        header = [u"%s: %s" % (k, v)
                  for (k, v) in preped_req.headers.items()
                  if k == u'Authorization']
        # Pull the URL, which includes query params
        url = preped_req.url
        return websocket.create_connection(url, header=header)

    def apply_authentication(self, req):
        if self.authenticator and self.authenticator.matches(req.url):
            self.authenticator.apply(req)


def preprocess_request_params(headers, data):
    # If body is dict/list, dump it as a string
    if headers and headers.get('content-type') == 'application/json':
        return data if isinstance(data, (str, unicode)) else json.dumps(data)
