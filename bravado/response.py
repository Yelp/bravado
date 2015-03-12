# -*- coding: utf-8 -*-

#
# Copyright (c) Yelp, Inc.
#

"""Code for checking the response from API. If correct, it proceeds to convert
it into Python class types
"""
from bravado.mapping.response import ResponseLike
from bravado.exception import CancelledError


DEFAULT_TIMEOUT_S = 5.0


# TODO: why is this messing with exceptions? It's not going to work with all
# http clients
def handle_response_errors(e):
    if hasattr(e, 'response') and hasattr(e.response, 'text'):
        # e.args is a tuple, change to list for modifications
        args = list(e.args)
        args[0] += (' : ' + e.response.text)
        e.args = tuple(args)
    raise e


class HTTPFuture(object):
    """A future which inputs HTTP params"""

    def __init__(self, http_client, request_params, post_receive):
        """Kicks API call for Asynchronous client

        :param http_client: a :class:`bravado.http_client.HttpClient`
        :param request_params: dict containing API request parameters
        :param post_receive: function to callback on finish
        """
        self._http_client = http_client
        self._post_receive = post_receive
        # A request is an EventualResult in the async client
        self._request = self._http_client.start_request(request_params)
        self._cancelled = False

    def cancelled(self):
        """Checks if API is cancelled
        Once cancelled, it can't be resumed
        """
        return self._cancelled

    def cancel(self):
        """Try to cancel the API (meaningful for Asynchronous client)
        """
        self._cancelled = True
        self._request.cancel()

    def result(self, **kwargs):
        """Blocking call to wait for API response
        If API was cancelled earlier, CancelledError is raised
        If everything goes fine, callback registered is triggered with response

        :param timeout: timeout in seconds to wait for response
        :type timeout: integer
        :param allow_null: if True, allow null fields in response
        :type allow_null: boolean
        :param raw_response: if True, return raw response w/o any validations
        :type raw_response: boolean
        """
        timeout = kwargs.pop('timeout', DEFAULT_TIMEOUT_S)

        if self.cancelled():
            raise CancelledError()
        response = self._request.result(timeout=timeout)
        try:
            if hasattr(response, 'raise_for_status'):
                response.raise_for_status()
        except Exception as e:
            handle_response_errors(e)

        return self._post_receive(response, **kwargs)


class RequestsResponseAdapter(ResponseLike):
    """Wraps a requests.models.Response object to provider a uniform interface
    to the response innards.

    :type requests_lib_response: :class:`requests.models.Response`
    """
    def __init__(self, requests_lib_response):
        self._delegate = requests_lib_response

    @property
    def status_code(self):
        return self._delegate.status_code

    def json(self, **kwargs):
        return self._delegate.json(**kwargs)


class FidoResponseAdapter(ResponseLike):
    """Wraps a fido.fido.Response object to provider a uniform interface
    to the response innards.

    :type requests_lib_response: :class:`fido.fido.Response`
    """
    def __init__(self, requests_lib_response):
        self._delegate = requests_lib_response

    @property
    def status_code(self):
        return self._delegate.code

    def json(self, **_):
        return self._delegate.json()
