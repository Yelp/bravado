# -*- coding: utf-8 -*-
import logging

from bravado_core.response import IncomingResponse
import requests
import requests.auth
from six.moves.urllib import parse as urlparse

from bravado.http_client import HttpClient
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

    @staticmethod
    def separate_params(request_params):
        """Splits the passed in dict of request_params into two buckets.

        - sanitized_params are valid kwargs for constructing a
          requests.Request(..)
        - misc_options are things like timeouts which can't be communicated
          to the Requests library via the requests.Request(...) constructor.

        :param request_params: kitchen sink of request params. Treated as a
            read-only dict.
        :returns: tuple(sanitized_params, misc_options)
        """
        sanitized_params = request_params.copy()
        misc_options = {}

        if 'connect_timeout' in sanitized_params:
            misc_options['connect_timeout'] = \
                sanitized_params.pop('connect_timeout')

        if 'timeout' in sanitized_params:
            misc_options['timeout'] = sanitized_params.pop('timeout')

        return sanitized_params, misc_options

    def request(self, request_params, response_callback=None,
                also_return_response=False):
        """
        :param request_params: complete request data.
        :type request_params: dict
        :param response_callback: Function to be called on the response
        :param also_return_response: Consult the constructor documentation for
            :class:`bravado.http_future.HttpFuture`.

        :returns: HTTP Future object
        :rtype: :class: `bravado_core.http_future.HttpFuture`
        """
        sanitized_params, misc_options = self.separate_params(request_params)

        requests_future = RequestsFutureAdapter(
            self.session,
            self.authenticated_request(sanitized_params),
            misc_options)

        return HttpFuture(
            requests_future,
            RequestsResponseAdapter,
            response_callback,
            also_return_response
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

    @property
    def reason(self):
        return self._delegate.reason

    @property
    def headers(self):
        return self._delegate.headers

    def json(self, **kwargs):
        return self._delegate.json(**kwargs)


class RequestsFutureAdapter(object):
    """Mimics a :class:`concurrent.futures.Future` for the purposes of making
    HTTP calls with the Requests library in a future-y sort of way.
    """

    def __init__(self, session, request, misc_options):
        """Kicks API call for Requests client

        :param session: session object to use for making the request
        :param request: dict containing API request parameters
        :param misc_options: misc options to apply when sending a HTTP request.
            e.g. timeout, connect_timeout, etc
        :type misc_options: dict
        """
        self.session = session
        self.request = request
        self.misc_options = misc_options

    def build_timeout(self, result_timeout):
        """
        Build the appropriate timeout object to pass to `session.send(...)`
        based on connect_timeout, the timeout passed to the service call, and
        the timeout passed to the result call.

        :param result_timeout: timeout that was passed into `future.result(..)`
        :return: timeout
        :rtype: float or tuple(connect_timeout, timeout)
        """
        # The API provides two ways to pass a timeout :( We're stuck
        # dealing with it until we're ready to make a non-backwards
        # compatible change.
        #
        #  - If both timeouts are the same, no problem
        #  - If either has a non-None value, use the non-None value
        #  - If both have a non-None value, use the greater of the two
        timeout = None
        has_service_timeout = 'timeout' in self.misc_options
        service_timeout = self.misc_options.get('timeout')

        if not has_service_timeout:
            timeout = result_timeout
        elif service_timeout == result_timeout:
            timeout = service_timeout
        else:
            if service_timeout is None:
                timeout = result_timeout
            elif result_timeout is None:
                timeout = service_timeout
            else:
                timeout = max(service_timeout, result_timeout)
            log.warn("Two different timeouts have been passed: "
                     "_request_options['timeout'] = {0} and "
                     "future.result(timeout={1}). Using timeout of {2}."
                     .format(service_timeout, result_timeout, timeout))

        # Requests is weird in that if you want to specify a connect_timeout
        # and idle timeout, then the timeout is passed as a tuple
        if 'connect_timeout' in self.misc_options:
            timeout = self.misc_options['connect_timeout'], timeout
        return timeout

    def result(self, timeout=None):
        """Blocking call to wait for API response

        :param timeout: timeout in seconds to wait for response. Defaults to
            None to wait indefinitely.
        :type timeout: float
        :return: raw response from the server
        :rtype: dict
        """
        request = self.request
        prepared_request = self.session.prepare_request(request)
        response = self.session.send(
            prepared_request,
            timeout=self.build_timeout(timeout))
        return response
