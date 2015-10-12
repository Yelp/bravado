Configuration
=============

You can configure certain behaviours when creating a ``SwaggerClient``.

The full documentation for each config key is in `bravado-core <http://bravado-core.readthedocs.org/en/latest/config.html>`_.

.. code-block:: python

    from bravado_core.formatter import SwaggerFormat
    from bravado.client import SwaggerClient

    my_super_duper_format = SwaggerFormat(...)

    config = {
        #  validate incoming responses
        'validate_responses': True,

        # validate outgoing requests
        'validate_requests': True,

        # validate the swagger spec
        'validate_swagger_spec': True

        # Use models (Python classes) instead of dicts for #/definitions/{models}
        'use_models': True

        # List of user-defined formats
        'formats': [my_super_duper_format]
    }

    client = SwaggerClient.from_url(..., config=config)
