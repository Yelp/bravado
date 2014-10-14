.. image:: https://travis-ci.org/Yelp/swagger-py.png?branch=master
  :target: https://travis-ci.org/Yelp/swagger-py?branch=master


Swagger-py
==========

About
-----

From Swagger's home page:

    Swagger is a specification and complete framework implementation for
    describing, producing, consuming, and visualizing RESTful web
    services.

Client libraries can automatically be generated from the `Swagger
specification <https://github.com/wordnik/swagger-core/wiki>`__, however Swagger-py
aims to be a compleate replacement for code generation (`swagger-codegen
<https://github.com/wordnik/swagger-codegen>`__).

Swagger.py is a forked from `digium/swagger-py <https://github.com/digium/swagger-py/>`__
for using `Swagger <https://developers.helloreverb.com/swagger/>`__ defined API's.

Example Usage
-------------

.. code:: Python

    from swaggerpy import client
    swagger_client = client.get_client("http://petstore.swagger.wordnik.com/api/api-docs")
    swagger_client.pet.getPetById(petId=42).result()

Documentation
-------------

More documentation is available at http://swagger-py.readthedocs.org

Installation
------------

::

    $ pip install --upgrade git+git://github.com/Yelp/swagger-py

Development
===========

Code is documented using `Sphinx <http://sphinx-doc.org/>`__.

`virtualenv <http://virtualenv.readthedocs.org/en/latest/virtualenv.html>`__. is
recommended to keep dependencies and libraries isolated.

Setup
-----

`Setuptools <http://pypi.python.org/pypi/setuptools>`__ is used for
building. `Nose <http://nose.readthedocs.org/en/latest/>`__ is used
for unit testing, with the `coverage
<http://nedbatchelder.com/code/coverage/>`__ plugin installed to
generated code coverage reports. Pass ``--with-coverage`` to generate
the code coverage report. HTML versions of the reports are put in
``cover/index.html``.

::

    $ ./setup.py develop   # prep for development (install deps, launchers, etc.)
    $ ./setup.py nosetests # run unit tests
    $ ./setup.py bdist_egg # build distributable

Testing
-------

Use `tox` to install and/or run tests living in `tests/`.

::

    $ tox

License
-------

Copyright (c) 2013, Digium, Inc. All rights reserved.
Copyright (c) 2014, Yelp, Inc. All rights reserved.

Swagger.py is licensed with a `BSD 3-Clause
License <http://opensource.org/licenses/BSD-3-Clause>`__.
