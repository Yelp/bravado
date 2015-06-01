# -*- coding: utf-8 -*-
import logging

from bravado_core.http_client import APP_FORM, HttpClient
from bravado_core.param import stringify_body as param_stringify_body
from bravado_core.response import IncomingResponse
import fido
from yelp_uri import urllib_utf8

from bravado.http_future import HttpFuture
from bravado.multipart_response import create_multipart_content

log = logging.getLogger(__name__)


class FidoResponseAdapter(IncomingResponse):
    """Wraps a fido.fido.Response object to provider a uniform interface
    to the response innards.

    :type fido_response: :class:`fido.fido.Response`
    """
    def __init__(self, fido_response):
        self._delegate = fido_response

    @property
    def status_code(self):
        return self._delegate.code

    @property
    def text(self):
        return self._delegate.body

    def json(self, **_):
        # TODO: pass the kwargs downstream
        return self._delegate.json()


class FidoClient(HttpClient):
    """Fido (Asynchronous) HTTP client implementation.
    """

    def request(self, request_params, response_callback=None):
        """Sets up the request params as per Twisted Agent needs.
        Sets up crochet and triggers the API request in background

        :param request_params: request parameters for API call
        :type request_params: dict
        :param response_callback: Function to be called after
        receiving the response
        :type response_callback: method

        :rtype: :class: `bravado_core.http_future.HttpFuture`
        """
        url = '%s?%s' % (request_params['url'], urllib_utf8.urlencode(
            request_params.get('params', []), True))

        request_params = {
            'method': str(request_params.get('method', 'GET')),
            'body': stringify_body(request_params),
            'headers': request_params.get('headers', {}),
        }

        return HttpFuture(fido.fetch(url, **request_params),
                          FidoResponseAdapter,
                          response_callback)


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
