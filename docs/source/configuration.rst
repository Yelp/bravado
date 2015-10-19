Configuration
=============

You can configure certain behaviours when creating a ``SwaggerClient``.

bravado and bravado-core use the same config dict. The full documentation for
`bravado-core config keys <http://bravado-core.readthedocs.org/en/latest/config.html>`_
is available too.

.. code-block:: python

    from bravado.client import SwaggerClient, SwaggerFormat

    my_super_duper_format = SwaggerFormat(...)

    config = {
        # === bravado config ===

        # Determines what is returned by the service call.
        'also_return_response': False,

        # === bravado-core config ====

        #  validate incoming responses
        'validate_responses': True,

        # validate outgoing requests
        'validate_requests': True,

        # validate the swagger spec
        'validate_swagger_spec': True,

        # Use models (Python classes) instead of dicts for #/definitions/{models}
        'use_models': True,

        # List of user-defined formats
        'formats': [my_super_duper_format],

    }

    client = SwaggerClient.from_url(..., config=config)


========================= =============== =========  ===============================================================
Config key                Type            Default    Description
------------------------- --------------- ---------  ---------------------------------------------------------------
*also_return_response*    boolean         False      | Determines what is returned by the service call.
                                                     | Specifically, the return value of ``HttpFuture.result()``.
                                                     | When ``False``, the swagger result is returned.
                                                     | When ``True``, the tuple ``(swagger result, http response)``
                                                     | is returned.
                                                     | See :ref:`getting_access_to_the_http_response`.
========================= =============== =========  ===============================================================
