# -*- coding: utf-8 -*-
import logging

import requests
import requests.auth
import requests.exceptions
import six
from bravado_core.response import IncomingResponse
from six import iteritems
from six.moves.urllib import parse as urlparse

from bravado.http_client import HttpClient
from bravado.http_future import FutureAdapter
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

    This authenticator adds an API key via query parameter or header.

    :param host: Host to authenticate for.
    :param api_key: API key.
    :param param_name: Query parameter specifying the API key.
    :param param_in: How to send the API key. Can be 'query' or 'header'.
    """

    def __init__(self, host, api_key, param_name=u'api_key', param_in=u'query'):
        super(ApiKeyAuthenticator, self).__init__(host)
        self.param_name = param_name
        self.param_in = param_in
        self.api_key = api_key

    def apply(self, request):
        if self.param_in == 'header':
            request.headers.setdefault(self.param_name, self.api_key)
        else:
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

    def __init__(self, ssl_verify=True, ssl_cert=None):
        """
        :param ssl_verify: Set to False to disable SSL certificate validation. Provide the path to a
            CA bundle if you need to use a custom one.
        :param ssl_cert: Provide a client-side certificate to use. Either a sequence of strings pointing
            to the certificate (1) and the private key (2), or a string pointing to the combined certificate
            and key.
        """
        self.session = requests.Session()
        self.authenticator = None
        self.ssl_verify = ssl_verify
        self.ssl_cert = ssl_cert

    def separate_params(self, request_params):
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
        misc_options = {
            'ssl_verify': self.ssl_verify,
            'ssl_cert': self.ssl_cert,
        }

        if 'connect_timeout' in sanitized_params:
            misc_options['connect_timeout'] = \
                sanitized_params.pop('connect_timeout')

        if 'timeout' in sanitized_params:
            misc_options['timeout'] = sanitized_params.pop('timeout')

        return sanitized_params, misc_options

    def request(self, request_params, operation=None, request_config=None):
        """
        :param request_params: complete request data.
        :type request_params: dict
        :param operation: operation that this http request is for. Defaults
            to None - in which case, we're obviously just retrieving a Swagger
            Spec.
        :type operation: :class:`bravado_core.operation.Operation`
        :param RequestConfig request_config: per-request configuration

        :returns: HTTP Future object
        :rtype: :class: `bravado_core.http_future.HttpFuture`
        """
        sanitized_params, misc_options = self.separate_params(request_params)

        requests_future = RequestsFutureAdapter(
            self.session,
            self.authenticated_request(sanitized_params),
            misc_options,
        )

        return HttpFuture(
            requests_future,
            RequestsResponseAdapter,
            operation,
            request_config,
        )

    def set_basic_auth(self, host, username, password):
        self.authenticator = BasicAuthenticator(
            host=host, username=username, password=password)

    def set_api_key(self, host, api_key, param_name=u'api_key',
                    param_in=u'query'):
        self.authenticator = ApiKeyAuthenticator(
            host=host, api_key=api_key, param_name=param_name,
            param_in=param_in)

    def authenticated_request(self, request_params):
        return self.apply_authentication(requests.Request(**request_params))

    def apply_authentication(self, request):
        if self.authenticator and self.authenticator.matches(request.url):
            return self.authenticator.apply(request)

        return request


class RequestsResponseAdapter(IncomingResponse):
    """Wraps a requests.models.Response object to provide a uniform interface
    to the response innards.

    :type requests_lib_response: :class:`requests.models.Response`
    """

    def __init__(self, requests_lib_response):
        self._delegate = requests_lib_response

    @property
    def status_code(self):
        return self._delegate.status_code

    @property
    def text(self):
        return self._delegate.text

    @property
    def raw_bytes(self):
        return self._delegate.content

    @property
    def reason(self):
        return self._delegate.reason

    @property
    def headers(self):
        return self._delegate.headers

    def json(self, **kwargs):
        return self._delegate.json(**kwargs)


class RequestsFutureAdapter(FutureAdapter):
    """Mimics a :class:`concurrent.futures.Future` for the purposes of making
    HTTP calls with the Requests library in a future-y sort of way.
    """

    timeout_errors = (requests.exceptions.ReadTimeout,)
    connection_errors = (requests.exceptions.ConnectionError,)

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
            log.warning(
                "Two different timeouts have been passed: "
                "_request_options['timeout'] = %s and "
                "future.result(timeout=%s). Using timeout of %s.",
                service_timeout, result_timeout, timeout,
            )

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

        # Ensure that all the headers are converted to strings.
        # This is need to workaround https://github.com/requests/requests/issues/3491
        request.headers = {
            k: str(v) if not isinstance(v, six.binary_type) else v
            for k, v in iteritems(request.headers)
        }

        prepared_request = self.session.prepare_request(request)
        settings = self.session.merge_environment_settings(
            prepared_request.url,
            None,
            None,
            self.misc_options['ssl_verify'],
            self.misc_options['ssl_cert'],
        )
        response = self.session.send(
            prepared_request,
            timeout=self.build_timeout(timeout),
            **settings
        )
        return response
