.. image:: https://travis-ci.org/Yelp/bravado.png?branch=master
  :target: https://travis-ci.org/Yelp/bravado?branch=master


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
aims to be a compleate replacement for code generation (`swagger-codegen
<https://github.com/wordnik/swagger-codegen>`__).

Bravado is a forked from `digium/swagger-py <https://github.com/digium/swagger-py/>`__
for using `Swagger <https://developers.helloreverb.com/swagger/>`__ defined API's.

Example Usage
-------------

.. code:: Python

    from bravado import client
    swagger_client = client.get_client("http://petstore.swagger.wordnik.com/api/api-docs")
    swagger_client.pet.getPetById(petId=42).result()

Documentation
-------------

More documentation is available at http://bravado.readthedocs.org

Installation
------------

::

    $ pip install --upgrade git+git://github.com/Yelp/bravado

Development
===========

Code is documented using `Sphinx <http://sphinx-doc.org/>`__.

`virtualenv <http://virtualenv.readthedocs.org/en/latest/virtualenv.html>`__. is
recommended to keep dependencies and libraries isolated.

Setup
-----

::

    tox


License
-------

Copyright (c) 2013, Digium, Inc. All rights reserved.
Copyright (c) 2014-2015, Yelp, Inc. All rights reserved.

Bravado is licensed with a `BSD 3-Clause
License <http://opensource.org/licenses/BSD-3-Clause>`__.
