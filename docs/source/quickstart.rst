Quickstart
===========================================

Usage
-----

Install the latest stable version from PyPi:

::

    $ pip install --upgrade bravado

.. _hello-pet:

Your first Hello World! (or Hello Pet)
--------------------------------------

Here is a simple example to try from a REPL (like IPython):

.. code-block:: python

    from bravado.client import SwaggerClient
    client = SwaggerClient.from_url("http://petstore.swagger.io/v2/swagger.json")
    pet = client.pet.getPetById(petId=42).result()

If you were lucky, and pet Id with 42 was present, you will get back a result.
It will be a dynamically created instance of ``bravado.model.Pet`` with attributes ``category``, etc. You can even try ``pet.category.id`` or ``pet.tags[0]``.

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
        swagger_client.pet.addPet(body=pet).result()


Time to get Twisted! (Asynchronous client)
------------------------------------------

``bravado`` provides an out of the box asynchronous http client with an optional timeout parameter.

:ref:`hello-pet` above can be rewritten to use the asynchronous `Fido <https://github.com/Yelp/fido>`_ client like so:

.. code-block:: python

        from bravado.client import SwaggerClient
        from bravado.fido_client import FidoClient
        client = SwaggerClient.from_url(
            "http://petstore.swagger.io/v2/swagger.json",
            FidoClient())
        result = client.pet.getPetById(petId=42).result(timeout=4)

.. note::

        ``timeout`` parameter here is the timeout (in seconds) the call will block waiting for the complete response. The default timeout is 5 seconds.

This is too fancy for me! I want a simple dict response!
------------------------------------------------------

``bravado`` has taken care of that as well. Configure the client to not use models.

.. code-block:: python

        from bravado.client import SwaggerClient
        from bravado.fido_client import FidoClient
        client = SwaggerClient.from_url(
            "http://petstore.swagger.io/v2/swagger.json",
            config={'use_models': False})
        result = client.pet.getPetById(petId=42).result(timeout=4)

Hello Pet response would look like::

        {'category': {'id': 0L, 'name': u''},
         'id': 2,
         'name': u'',
         'photoUrls': [u''],
         'status': u'',
         'tags': [{'id': 0L, 'name': u''}]}


Advanced options
================

Validations
-----------

``bravado`` validates the schema against the Swagger 2.0 Spec. Validations are also done on the requests and the responses.

Validation example:

.. code-block:: python

        pet = Pet(id="I should be integer :(", name="tommy")
        client.pet.addPet(body=pet).result()

will result in an error like so:

.. code-block:: console

        TypeError: id's value: 'I should be integer :(' should be in types (<type 'long'>, <type 'int'>)

.. note::

       If you'd like to disable validation of outgoing requests, you can set ``validate_requests`` to ``False`` in the ``config`` passed to ``SwaggerClient.from_url(...)``.

       The same hold for incoming responses with the ``validate_responses`` config option.

Adding Request Headers
----------------------

``bravado`` allows you to pass request headers along with any request.

.. code-block:: python

        Pet = client.get_model('Pet')
        Category = client.get_model('Category')
        pet = Pet(id=42, name="tommy", category=Category(id=24))
        swagger_client.pet.addPet(
            body=pet,
            _request_options={"headers": {"foo": "bar"}},
        ).result()


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

In the `Pet Store <http://petstore.swagger.io/>`_ example, operation ``findPetsByStatus`` has a ``default`` of ``available``. That means, ``bravado`` will plug that value in if no value is provided for the parameter. Example:

.. code-block:: python

        client.pet.findPetByStatus()

swagger.json from file path
-----------------------

``bravado`` also accepts ``swagger.json`` from a file path. Like so:

.. code-block:: python

        client = SwaggerClient.from_url('file:///some/path/swagger.json')

Other alternative way is by using helper method ``load_file``.

.. code-block:: python

        from bravado.swagger_model import load_file
        client = SwaggerClient.from_dict(load_file('/path/to/swagger.json'))
