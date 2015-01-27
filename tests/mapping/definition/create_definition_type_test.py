import pytest

from bravado.mapping.definition import create_definition_type


@pytest.fixture
def definition_dict():
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


def test_create_definition_type(definition_dict):
    definition_type = create_definition_type('Pet', definition_dict)
    expected = set(['id', 'category', 'name', 'photoUrls', 'status'])
    instance = definition_type(status='ok')
    assert set(vars(instance).keys()) == expected
    assert set(dir(instance)) == expected
    assert instance == definition_type(id=0, name='', status='ok')
    assert definition_type._swagger_types == {
        'id': 'integer:int64',
        'category': 'string',
        'name': 'string',
        'photoUrls': 'array:string',
        'status': 'string',
    }
    assert definition_type._required == ['name', 'photoUrls']


@pytest.mark.xfail(reason='TODO: fixme')
def test_create_definition_type_lazy_docstring(mocker, definition_dict):
    mock_create_docstring = mocker.patch(
        'bravado.mapping.docstring.create_definition_docstring', autospec=True)
    definition_type = create_definition_type('Pet', definition_dict)
    assert mock_create_docstring.call_count == 0
    assert definition_type.__doc__ == mock_create_docstring.return_value
    mock_create_docstring.assert_called_once_with(definition_dict['properties'])
