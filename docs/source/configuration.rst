Configuration
=============

Client Configuration
--------------------
You can configure certain behaviours when creating a ``SwaggerClient``.

bravado and bravado-core use the same config dict. The full documentation for
`bravado-core config keys <http://bravado-core.readthedocs.org/en/latest/config.html>`_
is available too.

.. code-block:: python

    from bravado.client import SwaggerClient, SwaggerFormat

    my_super_duper_format = SwaggerFormat(...)

    config = {
        # === bravado config ===

        # What class to use for response metadata
        'response_metadata_class': 'bravado.response.BravadoResponseMetadata',

        # Do not use fallback results even if they're provided
        'disable_fallback_results': False,

        # DEPRECATED: Determines what is returned by HttpFuture.result().
        # Please use HttpFuture.response() for accessing the http response.
        'also_return_response': False,

        # === bravado-core config ====

        # Validate incoming responses
        'validate_responses': True,

        # Validate outgoing requests
        'validate_requests': True,

        # Validate the swagger spec
        'validate_swagger_spec': True,

        # Use models (Python classes) instead of dicts for #/definitions/{models}
        'use_models': True,

        # List of user-defined formats
        'formats': [my_super_duper_format],

    }

    client = SwaggerClient.from_url(..., config=config)


========================== =============== ===============================================================
Config key                 Type            Description
-------------------------- --------------- ---------------------------------------------------------------
*response_metadata_class*  string          | The Metadata class to use; see
                                           | :ref:`custom_response_metadata` for details.
                                           Default: :class:`bravado.response.BravadoResponseMetadata`
*disable_fallback_results* boolean         | Whether to disable returning fallback results, even if
                                           | they're provided as an argument to
                                           | to :meth:`.HttpFuture.response`.
                                           Default: ``False``
*also_return_response*     boolean         | Determines what is returned by the service call.
                                           | Specifically, the return value of :meth:`.HttpFuture.result`.
                                           | When ``False``, the swagger result is returned.
                                           | When ``True``, the tuple ``(swagger result, http response)``
                                           | is returned. Has no effect on the return value of
                                           | :meth:`.HttpFuture.response`.
                                           | See :ref:`getting_access_to_the_http_response`.
                                           Default: ``False``
========================== =============== ===============================================================

Per-request Configuration
--------------------------
Configuration can also be applied on a per-request basis by passing in
``_request_options`` to the service call.

.. code-block:: python

    client = SwaggerClient.from_url(...)
    request_options = { ... }
    client.pet.getPetById(petId=42, _request_options=request_options).response().result

========================= =============== =========  ===============================================================
Config key                Type            Default    Description
------------------------- --------------- ---------  ---------------------------------------------------------------
*connect_timeout*         float           N/A        | TCP connect timeout in seconds. This is passed along to the
                                                     | http_client when making a service call.
*headers*                 dict            N/A        | Dict of http headers to to send with the outgoing request.
*response_callbacks*      list of         []         | List of callables that are invoked after the incoming
                          callables                  | response has been validated and unmarshalled but before being
                                                     | returned to the calling client. This is useful for client
                                                     | decorators that would like to hook into the post-receive
                                                     | event. The callables are executed in the order they appear
                                                     | in the list.
                                                     | Two parameters are passed to each callable:
                                                     | - ``incoming_response`` of type ``bravado_core.response.IncomingResponse``
                                                     | - ``operation`` of type ``bravado_core.operation.Operation``
*timeout*                 float           N/A        | TCP idle timeout in seconds. This is passed along to the
                                                     | http_client when making a service call.
*use_msgpack*             boolean         False      | If a msgpack serialization is desired for the response. This
                                                     | will add a Accept: application/msgpack header to the request.
*force_fallback_result*   boolean         False      | Whether a potentially provided fallback result should always
                                                     | be returned, regardless of whether the request succeeded.
                                                     | Mainly useful for manual and automated testing.
========================= =============== =========  ===============================================================
