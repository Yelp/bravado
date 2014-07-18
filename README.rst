About
-----

Swagger.py is a Python library forked from `digium/swagger-py <https://github.com/digium/swagger-py/>`__
for using `Swagger <https://developers.helloreverb.com/swagger/>`__ defined API's.

Swagger itself is best described on the Swagger home page:

    Swagger is a specification and complete framework implementation for
    describing, producing, consuming, and visualizing RESTful web
    services.

The `Swagger
specification <https://github.com/wordnik/swagger-core/wiki>`__ defines
how API's may be described using Swagger.


Features
--------

* A complete replacement to `swagger codegen <https://github.com/wordnik/swagger-codegen>`__ relieving user from technical debt codegen creates.
* Powered with tab complete feature on ``Resources`` and ``Operations`` on ipython
* Response models are converted to Python types and can be used to contruct request bodies.

    That means, ``JSON`` conversions can be completely removed from the code
* Requests and Responses are validated with Swagger spec 1.2
* Synchronous and Asynchronous HTTP clients are provided out of the box.
* A refetch of api-docs is performed before making API call if ``api-docs`` becomes stale than a specified time period.

    Also, caching of api-docs is done to avoid repetitive continous calls.
* Doc strings are provided for Operations and Models to give more information about the API
* Local File path to api-docs is also accepted by ``swagger-py``.

Usage
-----

Install directly from github as:

::

    $ pip install --upgrade git+git://github.com/Yelp/swagger-py

API
===

Here is a simple one to try from REPL:

.. code:: Python

    from swaggerpy import client
    swagger_client = swagger_client.get_client("http://petstore.swagger.wordnik.com/api/api-docs")
    client.pet.getPetById(petId=2).result(timeout=4)  # waits for 4 secs. for complete response
                                                      # else throws Timeout error. If timeout is
                                                      # not given, it will keep on waiting.


Which results in an instance of ``swaggerpy.swagger_model.Pet`` with attributes ``category``, etc.

To use Asynchronous HTTP client:

.. code:: Python

    from swaggerpy.async_http_client import AsynchronousHttpClient
    swagger_client = client.get_client("http://petstore.swagger.wordnik.com/api/api-docs",
                                       AsynchronousHttpClient())
    future = swagger_client.pet.getPetById(petId=2)
    # Some CPU intensive operations while responses are fetched
    result = future.result(timeout=5)  # waits for <timeout> seconds. (optional)


To use Python types in request body:

.. code:: Python

    from swaggerpy import client
    swagger_client = swagger_client.get_client("http://petstore.swagger.wordnik.com/api/api-docs")
    Pet = swagger_client.pet.models.Pet
    Category = swagger_client.pet.model.Category
    pet = Pet(id=34, category=Category(), name="TestTest")
    swagger_client.pet.addPet(body=pet).result()


Development
-----------

The code is documented using `Sphinx <http://sphinx-doc.org/>`__.

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

    $ ./tox  # runs the tests on Py26, Py27 and checks code formatting with flake8



License
-------

Copyright (c) 2013, Digium, Inc. 
Copyright (c) 2014, Yelp, Inc. All rights reserved.


Swagger.py is licensed with a `BSD 3-Clause
License <http://opensource.org/licenses/BSD-3-Clause>`__.
