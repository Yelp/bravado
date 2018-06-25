.. py:currentmodule:: bravado.testing.response_mocks

Testing code that uses bravado
==============================

Writing tests is crucial in making sure your code works and behaves as expected. bravado ships with two classes
that will help you create robust unit tests to verify the correctness of your code. We'll be using the excellent
`pytest <https://pytest.org/>`_ library in this example.

First of all, let's define the code we'd like to test:

.. code-block:: python

    from itertools import chain

    from bravado.client import SwaggerClient

    def get_available_pet_photos():
        petstore = SwaggerClient.from_url(
            'http://petstore.swagger.io/v2/swagger.json',
        )
        pets = petstore.pet.findPetsByStatus(status=['available']).response(
            timeout=0.5,
            fallback_result=lambda e: [],
        ).result

        return chain.from_iterable(pet.photoUrls for pet in pets)

First of all, in order to make sure your code doesn't do any network requests, you need to mock out the bravado client:

.. code-block:: python

    import mock
    import pytest

    from bravado.client import SwaggerClient

    @pytest.fixture
    def mock_client():
        mock_client = mock.Mock(name='mock SwaggerClient')
        with mock.patch.object(SwaggerClient, 'from_url', return_value=mock_client):
            yield mock_client

Now we can mock out that call to ``findPetsByStatus`` by using the
:class:`bravado.testing.response_mocks.BravadoResponseMock` class:

.. code-block:: python

    import mock

    from bravado.testing.response_mocks import BravadoResponseMock

    from mypackage import get_available_pet_photos

    def test_get_available_pet_photos(mock_client):
        mock_pets = [
            mock.Mock(
                photoUrls=['https://example.com/image.png'],
            ),
            mock.Mock(
                photoUrls=[
                    'https://example.com/image2.png',
                    'https://example.com/image3.png',
                ],
            ),
        ]

        mock_client.pet.findPetsByStatus.return_value.response = BravadoResponseMock(
            result=mock_pets,
        )

        pet_photos = get_available_pet_photos()

        assert list(pet_photos) == [
            'https://example.com/image.png',
            'https://example.com/image2.png',
            'https://example.com/image3.png',
        ]

Note that it's your responsibility to ensure that what you set as result for :class:`BravadoResponseMock` is
sufficiently similar to what bravado would return in production. We've used a ``Mock`` class here; another option
is to define namedtuples that correspond to your Swagger spec objects. This gives you even greater confidence
in the correctness of your code since access to undefined fields will result in an error.

Testing degraded responses
--------------------------

Use :class:`FallbackResultBravadoResponseMock` to test :ref:`fallback results <fallback_results>`. It works similarly,
but you don't have to pass the result to the constructor, since your fallback result callback will determine the result.
Let's add another test to verify our fallback result code path works properly:

.. code-block:: python

    from bravado.testing.response_mocks import FallbackResultBravadoResponseMock

    from example import get_available_pet_photos

    def test_get_available_pet_photos_fallback_result(mock_client):
        mock_client.pet.findPetsByStatus.return_value\
            .response = FallbackResultBravadoResponseMock()

        pet_photos = get_available_pet_photos()

        assert list(pet_photos) == []

Note that you can pass in a custom exception instance to :class:`.FallbackResultBravadoResponseMock` if you need
to trigger specific exception handling in your fallback result callback.

Setting custom response metadata
--------------------------------

Both :class:`.BravadoResponseMock` as well as :class:`.FallbackResultBravadoResponseMock` accept an optional
``metadata`` argument. Just pass in an instance of :class:`.BravadoResponseMetadata` that you'd like to be used.
A default one will be provided otherwise.
