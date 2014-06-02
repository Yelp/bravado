About
-----

Swagger.py is a Python library for using
`Swagger <https://developers.helloreverb.com/swagger/>`__ defined API's.

Swagger itself is best described on the Swagger home page:

    Swagger is a specification and complete framework implementation for
    describing, producing, consuming, and visualizing RESTful web
    services.

The `Swagger
specification <https://github.com/wordnik/swagger-core/wiki>`__ defines
how API's may be described using Swagger.

Swagger.py also supports a WebSocket extension, allowing a WebSocket to
be documented, and auto-generated WebSocket client code.

Usage
-----

Install directly from github as:

::

    $ pip install --upgrade git+git://github.com/Yelp/swagger-py

API
===

Here is a simple one to try from REPL:

.. code:: Python

    from swaggerpy.client import SwaggerClient
    client = SwaggerClient(u"http://petstore.swagger.wordnik.com/api/api-docs")
    client.pet.getPetById(petId=2).text


Data model
==========

The data model presented by the ``swagger_model`` module is nearly
identical to the original Swagger API resource listing and API
declaration. This means that if you add extra custom metadata to your
docs (such as a ``_author`` or ``_copyright`` field), they will carry
forward into the object model. I recommend prefixing custom fields with
an underscore, to avoid collisions with future versions of Swagger.

There are a few meaningful differences.

-  Resource listing
-  The ``file`` and ``base_dir`` fields have been added, referencing the
   original ``.json`` file.
-  The objects in a ``resource_listing``'s ``api`` array contains a
   field ``api_declaration``, which is the processed result from the
   referenced API doc.
-  API declaration
-  A ``file`` field has been added, referencing the original ``.json``
   file.

Development
-----------

The code is documented using `Sphinx <http://sphinx-doc.org/>`__, which
allows `IntelliJ IDEA <http://confluence.jetbrains.net/display/PYH/>`__
to do a better job at inferring types for autocompletion.

To keep things isolated, I also recommend installing (and using)
`virtualenv <http://www.virtualenv.org/>`__.

::

    $ sudo pip install virtualenv
    $ mkdir -p ~/virtualenv
    $ virtualenv ~/virtualenv/swagger
    $ . ~/virtualenv/swagger/bin/activate

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



License
-------

Copyright (c) 2013, Digium, Inc. All rights reserved.

Swagger.py is licensed with a `BSD 3-Clause
License <http://opensource.org/licenses/BSD-3-Clause>`__.
