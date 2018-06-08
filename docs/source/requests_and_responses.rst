Making requests with bravado
============================

When you call :meth:`.SwaggerClient.from_url` or :meth:`.SwaggerClient.from_spec`, Bravado takes a
Swagger (OpenAPI) 2.0 spec and returns a :class:`.SwaggerClient` instance that you can use to make
calls to the service described in the spec. You make calls by doing Python method calls in the form
of ``client.resource.operation(operation_params)``. Use ``dir(client)`` to see all available resources.

Resources and operations
------------------------

Resources are generated for each tag that exists in your Swagger spec. If an operation has no tags then
the left-most element of its path is taken as resource name. So in the case of an operation with the
path ``/pet/find``, ``pet`` will be the resource.

The operation name will be the (:ref:`sanitized <sanitizing_names>`) operationId value from the Swagger spec. If there is no
operationId, it will be generated. We highly recommend providing operation IDs for all operations.
Use ``dir(client.resource)`` to see a list of all available operations.

The operation method expects keyword arguments that have the same (:ref:`sanitized <sanitizing_names>`) names as in the Swagger spec.
Use corresponding Python types for the values - if the Swagger spec says a parameter is of type ``boolean``,
provide it as a Python ``bool``.

Futures and responses
---------------------

The return value of the operation method is a :class:`.HttpFuture`. To access the response, call :meth:`.HttpFuture.response()`.
This call will block, i.e. it will wait until the response is received or the timeout you specified is reached.

If the request succeeded and the server returned a HTTP status code between 200 and 399, the return value of
:meth:`.HttpFuture.response()` will be a :class:`~bravado.response.BravadoResponse` instance. You may access the Swagger
result of your call through :attr:`.BravadoResponse.result`.

If the server sent a response with a HTTP code of 400 or higher, by default a subclass of :class:`.HTTPError` will be raised
when you call :meth:`.HttpFuture.response`. The exception gives you access to the Swagger result (:attr:`.HTTPError.swagger_result`)
as well as the HTTP response object (:attr:`.HTTPError.response`).

Response metadata
-----------------

:attr:`.BravadoResponse.metadata` is an instance of :class:`.BravadoResponseMetadata` that provides you with access
to the HTTP response including headers and HTTP status code, request timings and whether a fallback result
was used (see :ref:`fallback_results`).

You're able to provide your own implementation of :class:`.BravadoResponseMetadata`; see :ref:`custom_response_metadata` for details.

.. _sanitizing_names:

Sanitizing names
----------------

Not all characters that the Swagger spec allows for names are valid Python identifiers. In particular,
spaces and the ``-`` character can be troublesome. bravado sanitizes resource, operation and parameter names
according to these rules:

- Any character that is not a letter or number is converted to an underscore (``_``)
- Collapse multiple consecutive underscores to one
- Remove leading and trailing underscores
- Remove leading numbers
