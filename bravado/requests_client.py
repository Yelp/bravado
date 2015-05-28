# -*- coding: utf-8 -*-
import logging
import sys
import urlparse

from bravado_core.http_client import HttpClient
from bravado_core.response import IncomingResponse
import requests
import requests.auth

from bravado.exception import HTTPError
from bravado.http_future import HttpFuture


log = logging.getLogger(__name__)


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

    def request(self, request_params, response_callback=None):
        """
        :param request_params: complete request data.
        :type request_params: dict
        :param response_callback: Function to be called on the response
        :returns: HTTP Future object
        :rtype: :class: `bravado_core.http_future.HttpFuture`
        """
        requests_future = RequestsFutureAdapter(
            self.session, self.authenticated_request(request_params))

        return HttpFuture(
            requests_future,
            RequestsResponseAdapter,
            response_callback,
            )

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


def add_response_detail_to_errors(e):
    """Specific to requests errors. Error detail is not
    directly visible in `raise_for_status` trace, instead it is
    located under `e.response.text`

    :param e: Exception object
    :type e: :class: `requests.HTTPError`
    :raises HTTPError: :class: `bravado.exception.HTTPError`
    """
    args = list(e.args)
    if hasattr(e, 'response') and hasattr(e.response, 'text'):
        args[0] += (' : ' + e.response.text)
    raise HTTPError(*args), None, sys.exc_info()[2]


class RequestsResponseAdapter(IncomingResponse):
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

    @property
    def text(self):
        return self._delegate.text

    def json(self, **kwargs):
        return self._delegate.json(**kwargs)


class RequestsFutureAdapter(object):
    """A future which inputs HTTP params"""

    def __init__(self, session, request):
        """Kicks API call for Requests client

        :param session: session object to use for making the request
        :param request: dict containing API request parameters
        """
        self.session = session
        self.request = request

    def check_for_exceptions(self, response):
        try:
            response.raise_for_status()
        except Exception as e:
            add_response_detail_to_errors(e)

    def result(self, timeout):
        """Blocking call to wait for API response

        :param timeout: timeout in seconds to wait for response
        :type timeout: integer
        :return: raw response from the server
        :rtype: dict
        """
        request = self.request
        response = self.session.send(
            self.session.prepare_request(request),
            timeout=timeout)

        self.check_for_exceptions(response)

        return response
