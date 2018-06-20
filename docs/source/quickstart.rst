Quickstart
==========

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
    pet = client.pet.getPetById(petId=42).response().result

If you were lucky, and pet Id with 42 was present, you will get back a result.
It will be a dynamically created instance of ``bravado.model.Pet`` with attributes ``category``, etc. You can even try ``pet.category.id`` or ``pet.tags[0]``.

Sample Response: ::

       Pet(category=Category(id=0L, name=u''), status=u'', name=u'', tags=[Tag(id=0L, name=u'')], photoUrls=[u''], id=2)

If you got a ``404``, try some other petId.


Lets try a POST call
--------------------

Here we will demonstrate how ``bravado`` hides all the ``JSON`` handling from the user, and makes the code more Pythonic.

.. code-block:: python

        Pet = client.get_model('Pet')
        Category = client.get_model('Category')
        pet = Pet(id=42, name="tommy", category=Category(id=24))
        client.pet.addPet(body=pet).response().result


Time to get Twisted! (Asynchronous client)
------------------------------------------

``bravado`` provides an out of the box asynchronous http client with an optional timeout parameter.

:ref:`hello-pet` above can be rewritten to use the asynchronous `Fido <https://github.com/Yelp/fido>`_ client like so:

.. code-block:: python

        from bravado.client import SwaggerClient
        from bravado.fido_client import FidoClient

        client = SwaggerClient.from_url(
            'http://petstore.swagger.io/v2/swagger.json',
            FidoClient()
        )

        result = client.pet.getPetById(petId=42).result(timeout=4)

.. note::

        ``timeout`` parameter here is the timeout (in seconds) the call will block waiting for the complete response. The default timeout is to wait indefinitely.

.. note::

        To use Fido client you should install bravado with fido extra via ``pip install bravado[fido]``.

This is too fancy for me! I want a simple dict response!
--------------------------------------------------------

``bravado`` has taken care of that as well. Configure the client to not use models.

.. code-block:: python

        from bravado.client import SwaggerClient
        from bravado.fido_client import FidoClient

        client = SwaggerClient.from_url(
            'http://petstore.swagger.io/v2/swagger.json',
            config={'use_models': False}
        )

        result = client.pet.getPetById(petId=42).result(timeout=4)

``result`` will look something like:

.. code-block:: javascript

        {
            'category': {
                'id': 0L,
                'name': u''
            },
            'id': 2,
            'name': u'',
            'photoUrls': [u''],
            'status': u'',
            'tags': [
                {'id': 0L, 'name': u''}
            ]
        }
