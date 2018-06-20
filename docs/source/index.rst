bravado documentation
========================

Bravado is a python client library for Swagger 2.0 services.

More information on Swagger can be found `on the Swagger website
<http://swagger.io/>`_

It aims to be a complete replacement to `swagger codegen <https://github.com/wordnik/swagger-codegen>`__.

Features include:

* Dynamically generated client - no code generation needed!

* `Synchronous <http://docs.python-requests.org/en/latest/>`_ and `Asynchronous <https://github.com/Yelp/fido>`_ http clients out of the box.

* Strict validations to verify that your Swagger Schema is  `v2.0 <https://github.com/wordnik/swagger-spec/blob/master/versions/2.0.md/>`_ compatible.

* HTTP request and response validation against your Swagger Schema.

* Swagger models as Python types (no need to deal with JSON).

* REPL friendly navigation of your Swagger schema with docstrings for Resources, Operations and Models.

* Ingestion of your Swagger schema via http or a local file path.

Contents:

.. toctree::
   :maxdepth: 1

   quickstart
   configuration
   requests_and_responses
   advanced
   testing
   modules
   changelog

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
