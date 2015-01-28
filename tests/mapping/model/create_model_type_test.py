import mock
import pytest

from bravado.mapping.model import create_model_type


@pytest.fixture
def model_dict():
    return {
        "required": [
            "name",
            "photoUrls"
        ],
        "properties": {
            "id": {
                "type": "integer",
                "format": "int64"
            },
            "category": {
                "type": "string"
            },
            "name": {
                "type": "string",
                "example": "doggie"
            },
            "photoUrls": {
                "type": "array",
                "xml": {
                    "name": "photoUrl",
                    "wrapped": True
                },
                "items": {
                    "type": "string"
                }
            },
            "status": {
                "type": "string",
                "description": "pet status in the store"
            }
        },
    }


def test_pet_model(model_dict):
    model_type = create_model_type('Pet', model_dict)
    expected = set(['id', 'category', 'name', 'photoUrls', 'status'])
    instance = model_type(status='ok')
    assert set(vars(instance).keys()) == expected
    assert set(dir(instance)) == expected
    assert instance == model_type(id=0, name='', status='ok')
    assert model_type._swagger_types == {
        'id': 'integer:int64',
        'category': 'string',
        'name': 'string',
        'photoUrls': 'array:string',
        'status': 'string',
    }
    assert model_type._required == ['name', 'photoUrls']


@mock.patch('bravado.mapping.model.create_model_docstring', autospec=True)
def test_create_model_type_lazy_docstring(mock_create_docstring):
    # NOTE: some sort of weird interaction with pytest, pytest-mock and mock
    #       made using the 'mocker' fixture here a no-go.
    pet_dict = model_dict()
    pet_type = create_model_type('Pet', pet_dict)
    assert not mock_create_docstring.called
    assert pet_type.__doc__ == mock_create_docstring.return_value
    mock_create_docstring.assert_called_once_with(pet_dict['properties'])