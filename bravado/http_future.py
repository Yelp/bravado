# -*- coding: utf-8 -*-
import sys
from functools import wraps

import six
from bravado_core.content_type import APP_JSON
from bravado_core.content_type import APP_MSGPACK
from bravado_core.exception import MatchingResponseNotFound
from bravado_core.response import get_response_spec
from bravado_core.unmarshal import unmarshal_schema_object
from bravado_core.validate import validate_schema_object
from msgpack import unpackb

from bravado.config_defaults import REQUEST_OPTIONS_DEFAULTS
from bravado.exception import BravadoTimeoutError
from bravado.exception import HTTPServerError
from bravado.exception import make_http_exception
from bravado.response import BravadoResponse


FALLBACK_EXCEPTIONS = (
    BravadoTimeoutError,
    HTTPServerError,
)


class FutureAdapter(object):
    """
    Mimics a :class:`concurrent.futures.Future` regardless of which client is
    performing the request, whether it is synchronous or actually asynchronous.

    This adapter must be implemented by all bravado clients such as FidoClient
    or RequestsClient to wrap the object returned by their 'request' method.

    """

    # Make sure to define the timeout errors associated with your http client
    timeout_errors = []

    def result(self, timeout=None):
        """
        Must implement a result method which blocks on result retrieval.

        :param timeout: maximum time to wait on result retrieval. Defaults to
            None which means blocking undefinitely.
        """
        raise NotImplementedError(
            "FutureAdapter must implement 'result' method"
        )


def reraise_errors(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        timeout_errors = tuple(getattr(self.future, 'timeout_errors', None) or ())

        # Make sure that timeout error type for a specific future adapter is generated only once
        if timeout_errors and getattr(self.future, '__timeout_error_type', None) is None:
            setattr(
                self.future, '__timeout_error_type',
                type(
                    '{}Timeout'.format(self.future.__class__.__name__),
                    tuple(list(timeout_errors) + [BravadoTimeoutError]),
                    dict(),
                ),
            )

        if timeout_errors:
            try:
                return func(self, *args, **kwargs)
            except timeout_errors as exception:
                six.reraise(
                    self.future.__timeout_error_type,
                    self.future.__timeout_error_type(*exception.args),
                    sys.exc_info()[2],
                )
        else:
            return func(self, *args, **kwargs)

    return wrapper


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
        self.response_callbacks = response_callbacks or REQUEST_OPTIONS_DEFAULTS['response_callbacks']
        self.also_return_response = also_return_response

    def response(self, timeout=None, fallback_response=None, exceptions_to_catch=FALLBACK_EXCEPTIONS):
        """Blocking call to wait for the HTTP response.

        :param timeout: Number of seconds to wait for a response. Defaults to
            None which means wait indefinitely.
        :type timeout: float
        :param fallback_response: callable that accepts an exception as argument and returns the
            swagger result to use in case of errors
        :type fallback_response: callable that takes an exception and returns a fallback swagger result
        :param exceptions_to_catch: Exception classes to catch and call `fallback_response`
            with. Has no effect if `fallback_response` is not provided. By default, `fallback_response`
            will be called for read timeout and server errors (HTTP 5XX).
        :type exceptions_to_catch: List/Tuple of Exception classes.
        :return: A BravadoResponse instance containing the swagger result and response metadata.
        """
        incoming_response = None
        try:
            incoming_response = self._get_incoming_response(timeout)
            swagger_result = self._get_swagger_result(incoming_response)
            if self.operation is None and incoming_response.status_code >= 300:
                raise make_http_exception(response=incoming_response)
        except exceptions_to_catch as e:
            if fallback_response:
                swagger_result = fallback_response(e)
            else:
                six.reraise(type(e), e, sys.exc_info()[2])

        return BravadoResponse(
            result=swagger_result,
            incoming_response=incoming_response,
        )

    def result(self, timeout=None):
        """DEPRECATED: please use the `response()` method instead.

        Blocking call to wait for and return the unmarshalled swagger result.

        :param timeout: Number of seconds to wait for a response. Defaults to
            None which means wait indefinitely.
        :type timeout: float
        :return: Depends on the value of also_return_response sent in
            to the constructor.
        """
        incoming_response = self._get_incoming_response(timeout)
        swagger_result = self._get_swagger_result(incoming_response)

        if self.operation is not None:
            if self.also_return_response:
                return swagger_result, incoming_response
            return swagger_result

        if 200 <= incoming_response.status_code < 300:
            return incoming_response

        raise make_http_exception(response=incoming_response)

    @reraise_errors
    def _get_incoming_response(self, timeout=None):
        inner_response = self.future.result(timeout=timeout)
        incoming_response = self.response_adapter(inner_response)
        return incoming_response

    def _get_swagger_result(self, incoming_response):
        swagger_result = None
        if self.operation is not None:
            unmarshal_response(
                incoming_response,
                self.operation,
                self.response_callbacks,
            )
            swagger_result = incoming_response.swagger_result

        return swagger_result


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
        incoming_response.swagger_result = unmarshal_response_inner(
            response=incoming_response,
            op=operation,
        )
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


def unmarshal_response_inner(response, op):
    """
    Unmarshal incoming http response into a value based on the
    response specification.
    :type response: :class:`bravado_core.response.IncomingResponse`
    :type op: :class:`bravado_core.operation.Operation`
    :returns: value where type(value) matches response_spec['schema']['type']
        if it exists, None otherwise.
    """
    deref = op.swagger_spec.deref
    response_spec = get_response_spec(status_code=response.status_code, op=op)

    if 'schema' not in response_spec:
        return None

    content_type = response.headers.get('content-type', '').lower()

    if content_type.startswith(APP_JSON) or content_type.startswith(APP_MSGPACK):
        content_spec = deref(response_spec['schema'])
        if content_type.startswith(APP_JSON):
            content_value = response.json()
        else:
            content_value = unpackb(response.raw_bytes, encoding='utf-8')

        if op.swagger_spec.config.get('validate_responses', False):
            validate_schema_object(op.swagger_spec, content_spec, content_value)

        return unmarshal_schema_object(
            swagger_spec=op.swagger_spec,
            schema_object_spec=content_spec,
            value=content_value,
        )

    # TODO: Non-json response contents
    return response.text


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
