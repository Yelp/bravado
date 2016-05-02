.. image:: https://img.shields.io/travis/Yelp/bravado.svg
  :target: https://travis-ci.org/Yelp/bravado?branch=master

.. image:: https://img.shields.io/coveralls/Yelp/bravado.svg
  :target: https://coveralls.io/r/Yelp/bravado

.. image:: https://img.shields.io/pypi/v/bravado.svg
    :target: https://pypi.python.org/pypi/bravado/
    :alt: PyPi version

.. image:: https://img.shields.io/pypi/pyversions/bravado.svg
    :target: https://pypi.python.org/pypi/bravado/
    :alt: Supported Python versions

Bravado
==========

About
-----

Bravado is a Yelp maintained fork of `digium/swagger-py <https://github.com/digium/swagger-py/>`__
for use with `OpenAPI Specification <https://github.com/OAI/OpenAPI-Specification>`__ (previously
known as Swagger).

From the OpenAPI Specification project:

    The goal of The OpenAPI Specification is to define a standard,
    language-agnostic interface to REST APIs which allows both humans and
    computers to discover and understand the capabilities of the service
    without access to source code, documentation, or through network traffic
    inspection.

Client libraries can automatically be generated from the OpenAPI specification,
however Bravado aims to be a complete replacement for code generation
(`swagger-codegen <https://github.com/wordnik/swagger-codegen>`__).

Example Usage
-------------

.. code:: Python

    from bravado.client import SwaggerClient
    client = SwaggerClient.from_url("http://petstore.swagger.io/v2/swagger.json")
    pet = client.pet.getPetById(petId=42).result()

Documentation
-------------

More documentation is available at http://bravado.readthedocs.org

Installation
------------

::

    $ pip install bravado

Development
===========

Code is documented using `Sphinx <http://sphinx-doc.org/>`__.

`virtualenv <http://virtualenv.readthedocs.org/en/latest/virtualenv.html>`__. is
recommended to keep dependencies and libraries isolated.

Setup
-----

::

    # Run tests
    tox
    # Install git pre-commit hooks
    .tox/py27/bin/pre-commit install


License
-------

Copyright (c) 2013, Digium, Inc. All rights reserved.
Copyright (c) 2014-2015, Yelp, Inc. All rights reserved.

Bravado is licensed with a `BSD 3-Clause
License <http://opensource.org/licenses/BSD-3-Clause>`__.
