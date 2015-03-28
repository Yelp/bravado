Quickstart
===========================================

Usage
-----

Install directly from github as:

::

    $ pip install --upgrade git+git://github.com/Yelp/bravado

.. _hello-pet:

Your first Hello World! (or Hello Pet)
--------------------------------------

Here is a simple one to try from REPL (like IPython):

.. code-block:: python

    from bravado.client import SwaggerClient
    client = SwaggerClient.from_url(
        "http://petstore.swagger.wordnik.com/api/api-docs")
    status, pet = client.pet.getPetById(petId=42).result()

If you were lucky, and pet Id with 42 was present, you will get back a result.
It will be an instance of ``bravado.swagger_model.Pet`` with attributes ``category``, etc. You can even try ``result.category.id`` or ``result.tags[0]``.

Sample Response: ::

       Pet(category=Category(id=0L, name=u''), status=u'', name=u'', tags=[Tag(id=0L, name=u'')], photoUrls=[u''], id=2)

If you got a ``404``, try some other petId.


Lets try a POST call
--------------------

Here we will demonstrate how ``bravado`` hides all the ``JSON`` handling from the user, and makes the code more Pythonic.

.. code-block:: python

        Pet = swagger_client.get_model('Pet')
        Category = swagger_client.get_model('Category')
        pet = Pet(id=42, name="tommy", category=Category(id=24))
        status, result = swagger_client.pet.addPet(body=pet).result()

It should give a ``200`` response like: ``{u'code': 200, u'message': u'SUCCESS'}``

Time to get Twisted! (Asynchronous client)
------------------------------------------

``bravado`` gives an out of the box asynchronous client to the user, with an optional timeout parameter.

:ref:`hello-pet` above can be rewritten to use asynchronous Fido client like so:

.. code-block:: python

        from bravado.client import SwaggerClient
        from bravado.fido_client import FidoClient
        client = SwaggerClient.from_url(
            "http://petstore.swagger.wordnik.com/api/api-docs",
            FidoClient())
        status, result = client.pet.getPetById(petId=42).result(timeout=4)

.. note::

        ``timeout`` parameter here is the timeout (in seconds) the call will block waiting for complete response. The default time is 5 seconds.

This is too fancy for me! I want simple dict response!
------------------------------------------------------

``bravado`` has taken care of that as well. ``result.as_dict()`` results in complete dict response.

Hello Pet response would look like::

        {'category': {'id': 0L, 'name': u''},
         'id': 2,
         'name': u'',
         'photoUrls': [u''],
         'status': u'',
         'tags': [{'id': 0L, 'name': u''}]}

.. note::

        ``result.__dict__`` returns only one level dict conversion, hence should be avoided.

Advanced options
================

Validations
-----------

``bravado`` validates the schema against the Swagger 2.0 Spec. Validations are also done on the requests and the responses.

Validation example:

.. code-block:: python

        pet = Pet(id="I should be integer :(", name="tommy")
        swagger_client.pet.addPet(body=pet).result()

will result in error like so:

.. code-block:: console

        TypeError: id's value: 'I should be integer :(' should be in types (<type 'long'>, <type 'int'>)

.. note::

       If you think it is acceptable for fields in your response to be null, and want the validator to ignore the type check you can add ``allow_null=True`` as a parameter to ``result()``.

       If response validations and type conversions are totally needed to be skipped, you can pass ``raw_response=True`` as a parameter to ``result()`` to get back raw API response.

Adding Request Headers
----------------------

``bravado`` allows you to pass request headers along with any request.

.. code-block:: python

        Pet = swagger_client.get_model('Pet')
        Category = swagger_client.get_model('Category')
        status, pet = Pet(id=42, name="tommy", category=Category(id=24))
        swagger_client.pet.addPet(
            body=pet,
            _request_options={"headers": {"foo": "bar"}},
        ).result()

Wrapping HTTP response error with custom class
----------------------------------------------

``bravado`` provided an option ``raise_with`` for wrapping HTTP errors with your custom Exception class. This is helpful for catching particular exception in your code or logging with particular exception class name.

.. code-block:: python

        class MyAwesomeException(Exception):
            pass

        swagger_client = SwaggerClient.from_url(
            "http://petstore.swagger.wordnik.com/api/api-docs",
            raise_with=MyAwesomeException)

Passing Headers to the api-docs requests
----------------------------------------------

``bravado`` provides an option to pass custom headers with requests to
api-docs

.. code-block:: python

        swagger_client = SwaggerClient.from_url(
            "http://petstore.swagger.wordnik.com/api/api-docs",
            api_doc_request_headers={'foo': 'bar'})

Docstrings
----------

``bravado`` provides docstrings to operations and models to quickly get the parameter and response types. A sample operation ``getPetById`` docstring looks like:

.. code-block:: console

        Docstring:
        [GET] Find pet by ID
        Returns a pet based on ID
        Args:
                petId (int64) : ID of pet that needs to be fetched
        Returns:
                Pet
        Raises:
                400: Invalid ID supplied
                404: Pet not found
        Class Docstring:Operation object.
        Call def:   c.pet.getPetById(self, kwargs)


Even the ``Pet`` model description can be found in the docstring:


.. code-block:: console

        Docstring:
        Attributes:
        category (Category)
        status (str) : pet status in the store
        name (str)
        tags (list(Tag))
        photoUrls (list(str))
        id (long) : unique identifier for the pet
        Constructor information:
          Definition:Pet(self, kwargs)


Default Values
--------------

``bravado`` uses the default values from the spec if the value is not provided in the request.

In the `Pet Store <http://petstore.swagger.wordnik.com/api/api-docs/pet/>`_ example, operation ``findPetByStatus`` has a ``defaultValue`` of ``available``. That means, ``bravado`` will plug that value if no value is provided for the parameter. Example:

.. code-block:: python

        swagger_client.pet.findPetByStatus()

Api-docs from file path
-----------------------

``bravado`` also accepts ``api-docs`` from file path. Like so:

.. code-block:: python

        client = SwaggerClient.from_url('file:///path/to/api-docs')

.. note::
        This needs a nested level file structure. Resources should be present under ``api-docs/``. File path should not have ``.json`` with the api-docs. It will be added by ``bravado``. This feature is still in beta phase.

Other alternative way is by using helper method ``load_file``. This doesn't need the resources to be nested.

.. code-block:: python

        from bravado.swagger_model import load_file
        client = SwaggerClient.from_dict(load_file('/path/to/api-docs'))

.. note::
        Both of the above methods also take an optional parameter ``api_base_path`` which can define the base path for the API call if basePath in schema is defined as '/'. It can be used like: ``SwaggerClient.from_url('file:///path/to/api-docs', api_base_path='http://foo')``
