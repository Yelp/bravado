Advanced Usage
==============

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
    ).result()


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

    pet = petstore.pet.getPetById(petId=42).result()
    print pet.name

However, there are times when it is necessary to have access to the actual
HTTP response so that the HTTP headers or HTTP status code can be used. This
is easily done via configuration to return a
``(swagger result, http response)`` tuple from the service call.

.. code-block:: python

    petstore = Swagger.from_url(..., config={'also_return_response': True})
    pet, http_response = petstore.pet.getPetById(petId=42).result()
    assert isinstance(http_response, bravado_core.response.IncomingResponse)
    print http_response.headers
    print http_response.status_code
    print pet.name
