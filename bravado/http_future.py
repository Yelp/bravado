# -*- coding: utf-8 -*-
import sys

import bravado_core
import six
from bravado_core.exception import MatchingResponseNotFound

from bravado.exception import make_http_exception


class FutureAdapter(object):
    """
    Mimics a :class:`concurrent.futures.Future` regardless of which client is
    performing the request, whether it is synchronous or actually asynchronous.

    This adapter must be implemented by all bravado clients such as FidoClient
    or RequestsClient to wrap the object returned by their 'request' method.

    """

    def result(self, timeout=None):
        """
        Must implement a result method which blocks on result retrieval.

        :param timeout: maximum time to wait on result retrieval. Defaults to
            None which means blocking undefinitely.
        """
        raise NotImplementedError(
            "FutureAdapter must implement 'result' method"
        )


class HttpFuture(object):
    """Wrapper for a :class:`FutureAdapter` that returns an HTTP response.

    :param future: The future object to wrap.
    :type future: :class: `FutureAdapter`
    :param response_adapter: Adapter type which exposes the innards of the HTTP
        response in a non-http client specific way.
    :type response_adapter: type that is a subclass of
        :class:`bravado_core.response.IncomingResponse`.
    :param response_callbacks: See bravado.client.REQUEST_OPTIONS_DEFAULTS
    :param also_return_response: Determines if the incoming http response is
        included as part of the return value from calling
        `HttpFuture.result()`.
        When False, only the swagger result is returned.
        When True, the tuple(swagger result, http response) is returned.
        This is useful if you want access to additional data that is not
        accessible from the swagger result. e.g. http headers,
        http response code, etc.
        Defaults to False for backwards compatibility.
    """

    def __init__(self, future, response_adapter, operation=None,
                 response_callbacks=None, also_return_response=False):
        self.future = future
        self.response_adapter = response_adapter
        self.operation = operation
        self.response_callbacks = response_callbacks or []
        self.also_return_response = also_return_response

    def result(self, timeout=None):
        """Blocking call to wait for the HTTP response.

        :param timeout: Number of seconds to wait for a response. Defaults to
            None which means wait indefinitely.
        :type timeout: float
        :return: Depends on the value of also_return_response sent in
            to the constructor.
        """
        inner_response = self.future.result(timeout=timeout)
        incoming_response = self.response_adapter(inner_response)

        if self.operation is not None:
            unmarshal_response(
                incoming_response,
                self.operation,
                self.response_callbacks)

            swagger_result = incoming_response.swagger_result
            if self.also_return_response:
                return swagger_result, incoming_response
            return swagger_result

        if 200 <= incoming_response.status_code < 300:
            return incoming_response

        raise make_http_exception(response=incoming_response)


def unmarshal_response(incoming_response, operation, response_callbacks=None):
    """So the http_client is finished with its part of processing the response.
    This hands the response over to bravado_core for validation and
    unmarshalling and then runs any response callbacks. On success, the
    swagger_result is available as ``incoming_response.swagger_result``.

    :type incoming_response: :class:`bravado_core.response.IncomingResponse`
    :type operation: :class:`bravado_core.operation.Operation`
    :type response_callbacks: list of callable. See
        bravado_core.client.REQUEST_OPTIONS_DEFAULTS.

    :raises: HTTPError
        - On 5XX status code, the HTTPError has minimal information.
        - On non-2XX status code with no matching response, the HTTPError
            contains a detailed error message.
        - On non-2XX status code with a matching response, the HTTPError
            contains the return value.
    """
    response_callbacks = response_callbacks or []

    try:
        raise_on_unexpected(incoming_response)
        incoming_response.swagger_result = \
            bravado_core.response.unmarshal_response(
                incoming_response,
                operation)
    except MatchingResponseNotFound as e:
        exception = make_http_exception(
            response=incoming_response,
            message=str(e)
        )
        six.reraise(
            type(exception),
            exception,
            sys.exc_info()[2])
    finally:
        # Always run the callbacks regardless of success/failure
        for response_callback in response_callbacks:
            response_callback(incoming_response, operation)

    raise_on_expected(incoming_response)


def raise_on_unexpected(http_response):
    """Raise an HTTPError if the response is 5XX.

    :param http_response: :class:`bravado_core.response.IncomingResponse`
    :raises: HTTPError
    """
    if 500 <= http_response.status_code <= 599:
        raise make_http_exception(response=http_response)


def raise_on_expected(http_response):
    """Raise an HTTPError if the response is non-2XX and matches a response
    in the swagger spec.

    :param http_response: :class:`bravado_core.response.IncomingResponse`
    :raises: HTTPError
    """
    if not 200 <= http_response.status_code < 300:
        raise make_http_exception(
            response=http_response,
            swagger_result=http_response.swagger_result)
