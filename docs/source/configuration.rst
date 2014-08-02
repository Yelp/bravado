Configuring swagger-py
======================

There are some configurations which can be handy.

.. code-block:: ini

        # Default time in seconds api-docs is cached
        swaggerpy.client.SWAGGER_SPEC_TIMEOUT_S = 300

        # Default timeout in seconds for client to get complete response
        swaggerpy.response.DEFAULT_TIMEOUT_S = 5.0
