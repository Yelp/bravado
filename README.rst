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

From Swagger's home page:

    Swagger is a specification and complete framework implementation for
    describing, producing, consuming, and visualizing RESTful web
    services.

Client libraries can automatically be generated from the `Swagger
specification <https://github.com/wordnik/swagger-core/wiki>`__, however Bravado
aims to be a complete replacement for code generation (`swagger-codegen
<https://github.com/wordnik/swagger-codegen>`__).

Bravado is a forked from `digium/swagger-py <https://github.com/digium/swagger-py/>`__
for using `Swagger <https://developers.helloreverb.com/swagger/>`__ defined API's.

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
