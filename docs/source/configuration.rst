Configuring bravado
======================

You can configure certain behaviours when creating a ``SwaggerClient``.

.. code-block:: python

    config = {
        #  validate incoming responses
        'validate_responses': True,

        # validate outgoing requests
        'validate_requests': True,

        # validate the swagger spec
        'validate_swagger_spec': True

        # Use models (Python classes) instead of dicts for #/definitions/{models}
        'use_models': True
    }

    client = SwaggerClient.from_url(..., config=config)
