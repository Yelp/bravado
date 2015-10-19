# -*- coding: utf-8 -*-
import logging
import json
import bitjws
import requests
import requests.auth
from bravado.requests_client import *

from bravado.http_client import HttpClient
from bravado.http_future import HttpFuture

log = logging.getLogger(__name__)


class BitJWSAuthenticator(Authenticator):
    """BitJWS authenticator uses JWS and the CUSTOM-BITCOIN-SIGN algorithm.

    :param host: Host to authenticate for.
    :param privkey: Private key as a WIF string
    """

    def __init__(self, host, privkey):
        super(BitJWSAuthenticator, self).__init__(host)
        self.privkey = bitjws.PrivateKey(bitjws.wif_to_privkey(privkey))

    def apply(self, request):
        if len(request.data) > 0:
            data = bitjws.sign_serialize(self.privkey, **json.loads(request.data))
        else:
            data = bitjws.sign_serialize(self.privkey, **request.params)
        request.params = {}
        request.data = data
        return request


class BitJWSRequestsClient(HttpClient):
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

    def request(self, request_params, response_callback=None):
        """
        :param request_params: complete request data.
        :type request_params: dict
        :param response_callback: Function to be called on the response
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
            BitJWSRequestsResponseAdapter,
            response_callback,
        )

    def set_basic_auth(self, host, username, password):
        self.authenticator = BasicAuthenticator(
            host=host, username=username, password=password)

    def set_api_key(self, host, api_key, param_name=u'api_key'):
        self.authenticator = ApiKeyAuthenticator(
            host=host, api_key=api_key, param_name=param_name)

    def set_bitjws_key(self, host, privkey):
        self.authenticator = BitJWSAuthenticator(host=host, privkey=privkey)

    def authenticated_request(self, request_params):
        return self.apply_authentication(requests.Request(**request_params))

    def apply_authentication(self, request):
        if self.authenticator and self.authenticator.matches(request.url):
            return self.authenticator.apply(request)
        return request


class BitJWSRequestsResponseAdapter(IncomingResponse):
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

    def json(self, **kwargs):
        if 'content-type' in self._delegate.headers and \
                'json' in self._delegate.headers['content-type']:
            jso = self._delegate.json(**kwargs)
        else:
            rawtext = self.text.decode('utf8')
            headers, jso = bitjws.validate_deserialize(rawtext)
        return jso

