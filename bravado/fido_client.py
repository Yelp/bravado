# -*- coding: utf-8 -*-
import logging
import sys

import crochet
import fido
import fido.exceptions
import requests
import requests.structures
import six
import twisted.internet.error
import twisted.web.client
from bravado_core.response import IncomingResponse
from yelp_bytes import to_bytes

from bravado.http_client import HttpClient
from bravado.http_future import FutureAdapter
from bravado.http_future import HttpFuture

log = logging.getLogger(__name__)


class FidoResponseAdapter(IncomingResponse):
    """Wraps a fido.fido.Response object to provide a uniform interface
    to the response innards.

    :type fido_response: :class:`fido.fido.Response`
    """

    def __init__(self, fido_response):
        self._delegate = fido_response
        self._headers = None

    @property
    def status_code(self):
        return self._delegate.code

    @property
    def text(self):
        return self._delegate.body

    @property
    def raw_bytes(self):
        return self._delegate.body

    @property
    def reason(self):
        return self._delegate.reason

    @property
    def headers(self):
        # Header names and values are bytestrings, which is an issue on Python 3. Additionally,
        # header values are lists of strings. This is incompatible with how requests returns headers.
        # Let's match the requests interface so code dealing with headers continues to work even when
        # you change the HTTP client.
        if not self._headers:
            self._headers = requests.structures.CaseInsensitiveDict()
            for header, values in self._delegate.headers.items():
                # header names are encoded using latin1, while header values are encoded using UTF-8.
                # We'll take the last entry in the list of values, making sure the latest header sent
                # takes precedence. The fact that twisted uses lists of strings for values seems to be
                # an edge case, I couldn't find any documentation or test using more than one entry in
                # the list of values for a given header.
                self._headers[header.decode('latin1')] = values[-1].decode('utf8')

        return self._headers

    def json(self, **_):
        # TODO: pass the kwargs downstream
        return self._delegate.json()


class FidoClient(HttpClient):
    """Fido (Asynchronous) HTTP client implementation.
    """

    def request(self, request_params, operation=None, request_config=None):
        """Sets up the request params as per Twisted Agent needs.
        Sets up crochet and triggers the API request in background

        :param request_params: request parameters for the http request.
        :type request_params: dict
        :param operation: operation that this http request is for. Defaults
            to None - in which case, we're obviously just retrieving a Swagger
            Spec.
        :type operation: :class:`bravado_core.operation.Operation`
        :param RequestConfig request_config: per-request configuration

        :rtype: :class: `bravado_core.http_future.HttpFuture`
        """

        request_for_twisted = self.prepare_request_for_twisted(request_params)

        future_adapter = FidoFutureAdapter(fido.fetch(**request_for_twisted))

        return HttpFuture(future_adapter,
                          FidoResponseAdapter,
                          operation,
                          request_config)

    @staticmethod
    def prepare_request_for_twisted(request_params):
        """
        Uses the python package 'requests' to prepare the data as per twisted
        needs. requests.PreparedRequest.prepare is able to compute the body and
        the headers for the http call based on the input request_params. This
        contains any query parameters, files, body and headers to include.

        :return: dictionary in the form
            {
                'body': string,  # (can represent any content-type i.e. json,
                    file, multipart..),
                'headers': dictionary,  # headers->values
                'method': string,  # can be 'GET', 'POST' etc.
                'url': string,
                'timeout': float,  # optional
                'connect_timeout': float,  # optional
            }
        """

        prepared_request = requests.PreparedRequest()

        # Ensure that all the headers are converted to strings.
        # This is need to workaround https://github.com/requests/requests/issues/3491
        request_params['headers'] = {
            k: v if isinstance(v, six.binary_type) else str(v)
            for k, v in six.iteritems(request_params.get('headers', {}))
        }

        prepared_request.prepare(
            headers=request_params.get('headers'),
            data=request_params.get('data'),
            params=request_params.get('params'),
            files=request_params.get('files'),
            url=request_params.get('url'),
            method=request_params.get('method')
        )

        # content-length was computed by 'requests' based on the current body
        # but body will be processed by fido using twisted FileBodyProducer
        # causing content-length to lose meaning and break the client.
        prepared_request.headers.pop('Content-Length', None)

        request_for_twisted = {
            # converting to string for `requests` method is necessary when
            # using requests < 2.8.1 due to a bug while handling unicode values
            # See changelog 2.8.1 at https://pypi.python.org/pypi/requests
            'method': str(prepared_request.method or 'GET'),
            'body': (
                to_bytes(prepared_request.body)
                if prepared_request.body is not None else None
            ),
            'headers': prepared_request.headers,
            'url': prepared_request.url,
        }

        for fetch_kwarg in ('connect_timeout', 'timeout', 'tcp_nodelay'):
            if fetch_kwarg in request_params:
                request_for_twisted[fetch_kwarg] = request_params[fetch_kwarg]

        return request_for_twisted


class FidoFutureAdapter(FutureAdapter):
    """
    This is just a wrapper for an EventualResult object from crochet.
    It implements the 'result' method which is needed by our HttpFuture to
    retrieve results.
    """

    timeout_errors = (fido.exceptions.HTTPTimeoutError,)
    connection_errors = (
        fido.exceptions.TCPConnectionError,
        twisted.internet.error.ConnectingCancelledError,
        twisted.internet.error.DNSLookupError,
        twisted.web.client.RequestNotSent,
    )

    def __init__(self, eventual_result):
        self._eventual_result = eventual_result

    def result(self, timeout=None):
        try:
            return self._eventual_result.wait(timeout=timeout)
        except crochet.TimeoutError:
            self._eventual_result.cancel()
            six.reraise(
                fido.exceptions.HTTPTimeoutError,
                fido.exceptions.HTTPTimeoutError(
                    'Connection was closed by fido after blocking for '
                    'timeout={timeout} seconds waiting for the server to '
                    'send the response'.format(timeout=timeout)
                ),
                sys.exc_info()[2],
            )
