Changelog-Master
================

.. _PR32: https://github.com/Yelp/bravado/pull/32

- Show the response text when an unexpected 5xx response is returned. This fixes the regression for PR32_.
- Allow custom future and response adapter classes in both ``RequestsClient`` and ``FidoClient``.
