.. swagger-py documentation master file, created by
   sphinx-quickstart on Wed Oct 16 09:33:48 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to swagger-py's documentation!
======================================

This project acts as a generic client library for services which follow *Swagger* schema.

More information on Swagger can be found `on the Swagger website
<https://developers.helloreverb.com/swagger/>`_

It aims to be a complete replacement to `swagger codegen <https://github.com/wordnik/swagger-codegen>`__.

Features include:

* Synchronous and Asynchronous clients out of the box.
 
* Caching of api-docs with regular staleness check.

* Strict validations to check swagger spec is `v1.2 <https://github.com/wordnik/swagger-spec/blob/master/versions/1.2.md/>`_ compatible.

* Validations on the parameter and response types.

* Request and Response values are handled with Python types (no need to deal with JSON).

* Doc strings are provided for Operations and Models to give more information about the API.

* Local file path to api-docs is also acceptable.

Contents:

.. toctree::
   :maxdepth: 1

   quickstart
   changelog
   configuration
   swaggerpy

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

