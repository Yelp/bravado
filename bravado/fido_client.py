# -*- coding: utf-8 -*-
import logging

import six

if six.PY3:
    raise ImportError("The fido client is not yet supported in py3")

import fido
from bravado_core.param import stringify_body as param_stringify_body
from bravado_core.response import IncomingResponse
from yelp_uri import urllib_utf8

from bravado.http_client import APP_FORM, HttpClient
from bravado.http_future import HttpFuture
from bravado.multipart_response import create_multipart_content

log = logging.getLogger(__name__)


class FidoResponseAdapter(IncomingResponse):
    """Wraps a fido.fido.Response object to provide a uniform interface
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

    @property
    def reason(self):
        return self._delegate.reason

    @property
    def headers(self):
        return self._delegate.headers

    def json(self, **_):
        # TODO: pass the kwargs downstream
        return self._delegate.json()


class FidoClient(HttpClient):
    """Fido (Asynchronous) HTTP client implementation.
    """

    def request(self, request_params, operation=None, response_callbacks=None,
                also_return_response=False):
        """Sets up the request params as per Twisted Agent needs.
        Sets up crochet and triggers the API request in background

        :param request_params: request parameters for the http request.
        :type request_params: dict
        :param operation: operation that this http request is for. Defaults
            to None - in which case, we're obviously just retrieving a Swagger
            Spec.
        :type operation: :class:`bravado_core.operation.Operation`
        :param response_callbacks: List of callables to post-process the
            incoming response. Expects args incoming_response and operation.
        :param also_return_response: Consult the constructor documentation for
            :class:`bravado.http_future.HttpFuture`.

        :rtype: :class: `bravado_core.http_future.HttpFuture`
        """
        url = '%s?%s' % (request_params['url'], urllib_utf8.urlencode(
            request_params.get('params', []), True))

        fetch_kwargs = {
            'method': str(request_params.get('method', 'GET')),
            'body': stringify_body(request_params),
            'headers': request_params.get('headers', {}),
        }

        for fetch_kwarg in ('connect_timeout', 'timeout'):
            if fetch_kwarg in request_params:
                fetch_kwargs[fetch_kwarg] = request_params[fetch_kwarg]

        concurrent_future = fido.fetch(url, **fetch_kwargs)

        return HttpFuture(concurrent_future,
                          FidoResponseAdapter,
                          operation,
                          response_callbacks,
                          also_return_response)


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
