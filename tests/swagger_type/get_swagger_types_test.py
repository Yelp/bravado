from bravado.swagger_type import get_swagger_types


def test_empty():
    assert {} == get_swagger_types({})


def test_simple():
    props = {
        "id": {
            "type": "integer",
            "format": "int64"
        },
        "name": {
            "type": "string"
        }
    }
    expected = {
        'id': 'integer:int64',
        'name': 'string'
    }
    assert expected == get_swagger_types(props)
