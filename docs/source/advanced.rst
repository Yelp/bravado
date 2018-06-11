Advanced Usage
==============

Validations
-----------

``bravado`` validates the schema against the Swagger 2.0 Spec. Validations are also done on the requests and the responses.

Validation example:

.. code-block:: python

    pet = Pet(id="I should be integer :(", name="tommy")
    client.pet.addPet(body=pet).response().result

will result in an error like so:

.. code-block:: console

    TypeError: id's value: 'I should be integer :(' should be in types (<type 'long'>, <type 'int'>)

.. note::

   If you'd like to disable validation of outgoing requests, you can set ``validate_requests`` to ``False`` in the ``config`` passed to ``SwaggerClient.from_url(...)``.

   The same holds true for incoming responses with the ``validate_responses`` config option.

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
    ).response().result


Docstrings
----------

``bravado`` provides docstrings to operations and models to quickly get the parameter and response types.
Due to an implementation limitation, an operation's docstring looks like a class docstring instead of a
function docstring. However, the most useful information about parameters and return type is present
in the ``Docstring`` section.

.. note::

    The ``help`` built-in does not work as expected for docstrings. Use the ``?`` method instead.

.. code-block:: console

    >> petstore.pet.getPetById?

    Type:       CallableOperation
    String Form:<bravado.client.CallableOperation object at 0x241b5d0>
    File:       /some/dir/bravado/bravado/client.py
    Definition: c.pet.getPetById(self, **op_kwargs)
    Docstring:
    [GET] Find pet by ID

    Returns a single pet

    :param petId: ID of pet to return
    :type petId: integer
    :returns: 200: successful operation
    :rtype: object
    :returns: 400: Invalid ID supplied
    :returns: 404: Pet not found
    Constructor Docstring::type operation: :class:`bravado_core.operation.Operation`
    Call def:   c.pet.getPetById(self, **op_kwargs)
    Call docstring:
    Invoke the actual HTTP request and return a future that encapsulates
    the HTTP response.

    :rtype: :class:`bravado.http_future.HTTPFuture`

Docstrings for models can be retrieved as expected:

.. code-block:: console

    >> pet_model = petstore.get_model('Pet')
    >> pet_model?

    Type:       type
    String Form:<class 'bravado_core.model.Pet'>
    File:       /some/dir/bravado_core/model.py
    Docstring:
    Attributes:

    category: Category
    id: integer
    name: string
    photoUrls: list of string
    status: string - pet status in the store
    tags: list of Tag
    Constructor information:
     Definition:pet_type(self, **kwargs)

Default Values
--------------

``bravado`` uses the default values from the spec if the value is not provided in the request.

In the `Pet Store <http://petstore.swagger.io/>`_ example, operation ``findPetsByStatus`` has a ``default`` of ``available``. That means, ``bravado`` will plug that value in if no value is provided for the parameter.

.. code-block:: python

    client.pet.findPetByStatus()

Loading swagger.json by file path
---------------------------------

``bravado`` also accepts ``swagger.json`` from a file path. Like so:

.. code-block:: python

    client = SwaggerClient.from_url('file:///some/path/swagger.json')

Alternatively, you can also use the ``load_file`` helper method.

.. code-block:: python

    from bravado.swagger_model import load_file

    client = SwaggerClient.from_spec(load_file('/path/to/swagger.json'))

.. _getting_access_to_the_http_response:

Getting access to the HTTP response
-----------------------------------

The default behavior for a service call is to return the swagger result like so:

.. code-block:: python

    pet = petstore.pet.getPetById(petId=42).response().result
    print pet.name

However, there are times when it is necessary to have access to the actual
HTTP response so that the HTTP headers or HTTP status code can be used. Simply save
the response object (which is a :class:`.BravadoResponse`) and use its ``incoming_response``
attribute to access the incoming response:

.. code-block:: python

    petstore = Swagger.from_url(
        'http://petstore.swagger.io/swagger.json',
        config={'also_return_response': True},
    )
    pet_response = petstore.pet.getPetById(petId=42).response()
    http_response = pet_response.incoming_response
    assert isinstance(http_response, bravado_core.response.IncomingResponse)
    print http_response.headers
    print http_response.status_code
    print pet.name

.. _fallback_results:

Working with fallback results
-----------------------------

By default, if the server returns an error or doesn't respond in time, you have to catch and handle
the resulting exception accordingly. A simpler way would be to use the support for fallback results
provided by :meth:`.HttpFuture.response`.

:meth:`.HttpFuture.response` takes an optional argument ``fallback_result`` which is a callable
that returns a Swagger result. The callable takes one mandatory argument: the exception that would
have been raised normally. This allows you to return different results based on the type of error
(e.g. a :class:`.BravadoTimeoutError`) or, if a server response was received, on any data pertaining
to that response, like the HTTP status code.

In the simplest case, you can just specify what you're going to return:

.. code-block:: python
    petstore = Swagger.from_url('http://petstore.swagger.io/swagger.json')
    response = petstore.pet.findPetsByStatus(status=['available']).response(
        timeout=0.5,
        fallback_result=lambda e: [],
    )

This code will return an empty list in case the server doesn't respond quickly enough (or it
responded quickly enough, but returned an error).

But what if you're using models (the default) and the endpoint you're calling returns one? You'll have
to return one as well from your fallback_result function to stay compatible with the rest of your code:

.. code-block:: python
    petstore = Swagger.from_url('http://petstore.swagger.io/swagger.json')
    response = petstore.pet.getPetById(petId=101).response(
        timeout=0.5,
        fallback_result=lambda e: petstore.get_model('Pet')(name='No Pet found', photoUrls=[]),
    )

Two things to note here: first, use :meth:`.SwaggerClient.get_model` to get the model class for a
model name. Second, since ``name`` and ``photoUrls`` are required fields for this model, we probably should not leave them
empty (if we do they'd still be accessible, but the value would be ``None``). It's up to you how you decide to deal
with this case.

:attr:`.BravadoResponseMetadata.is_fallback_result` will be True if a fallback result has been returned
by the call to :meth:`.HttpFuture.response`.

.. _custom_response_metadata:

Custom response metadata
------------------------

Sometimes, there's additional metadata in the response that you'd like to make available easily.
This case arises most often if you're using bravado to talk to internal services. Maybe you have
special HTTP headers that indicate whether a circuit breaker was triggered? bravado allows you to
customize the metadata and provide custom attributes and methods.

In your code, create a class that subclasses :class:`bravado.response.BravadoResponseMetadata`. In the implementation
of your properties, use :attr:`.BravadoResponseMetadata.headers` to access response headers, or
:attr:`.BravadoResponseMetadata.incoming_response` to access any other part of the HTTP response.

If, for some reason, you need your own ``__init__`` method, make sure you have the same signature
as the base method and that you call it (the base method) from your own implementation.
