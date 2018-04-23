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
from bravado.exception import make_http_exception


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

    @reraise_errors
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

        result = unmarshal_schema_object(
            swagger_spec=op.swagger_spec,
            schema_object_spec=content_spec,
            value=content_value,
        )

        if op.swagger_spec.config.get('add_fetch_link', False):
            wrap_linked_objects_with_fetch(op, result, content_spec)

        return result
    # TODO: Non-json response contents
    return response.text


def wrap_linked_objects_with_fetch(op, result, content_spec):
    """
    Wraps any returned results that have a x-operationId property
    with a wrapper that allows the object to be callable to retrieve
    the linked resource.
    You can use both obj() and obj._fetch_linked() to access
    the http_request for the linked resource.
    """

    for key in result:
        properties = content_spec['properties'].get(key)
        linked_op_id = properties.get('x-operationId')
        if (linked_op_id and result[key]
            and properties.get('type') == 'string'
                and properties.get('format') == 'url'):

            linked_op = op.swagger_spec._client._get_operation(linked_op_id)

            if linked_op:
                result[key] = FetchLink(result[key], op=linked_op)
            else:
                # XXX find more appropriate exception
                raise NotImplementedError("x-operationId: {} NOT FOUND".format(linked_op_id))


class FetchLink(object):
    """
    This class makes an url object callable.

    You can use both obj() and obj._fetch_linked() to access
    the http_request for the linked resource.
    """

    def __init__(self, url, op):
        self._url = str(url)
        self._linked_operation = op

    def __str__(self):
        return self._url

    def __repr__(self):
        return "{}({},{})".format(self.__class__.__name__, self._url, str(self._linked_operation))

    def __call__(self):
        return self._fetch_linked()

    def _fetch_linked(self):
        op = self._linked_operation

        http_client = op.swagger_spec.http_client
        return http_client.request({'method': 'GET', 'url': str(self)},
                                   operation=op,
                                   also_return_response=op.swagger_spec.config.get('also_return_response'))


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
