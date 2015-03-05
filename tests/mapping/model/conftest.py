import pytest

from bravado.mapping.model import create_model_type


@pytest.fixture
def definitions_spec():
    return {
        "User": {
            "properties": {
                "id": {
                    "type": "integer",
                    "format": "int64"
                },
                "username": {
                    "type": "string"
                },
                "firstName": {
                    "type": "string"
                },
                "lastName": {
                    "type": "string"
                },
                "email": {
                    "type": "string"
                },
                "password": {
                    "type": "string"
                },
                "phone": {
                    "type": "string"
                },
                "userStatus": {
                    "type": "integer",
                    "format": "int32",
                    "description": "User Status"
                }
            },
            "xml": {
                "name": "User"
            }
        },
        "Category": {
            "properties": {
                "id": {
                    "type": "integer",
                    "format": "int64"
                },
                "name": {
                    "type": "string"
                }
            },
        },
        "Pet": {
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
                    "$ref": "#/definitions/Category"
                },
                "name": {
                    "type": "string",
                    "example": "doggie"
                },
                "photoUrls": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    }
                },
                "tags": {
                    "type": "array",
                    "items": {
                        "$ref": "#/definitions/Tag"
                    }
                },
            },
        },
        "Tag": {
            "properties": {
                "id": {
                    "type": "integer",
                    "format": "int64"
                },
                "name": {
                    "type": "string"
                }
            },
            "xml": {
                "name": "Tag"
            }
        },
    }


@pytest.fixture
def user_spec(definitions_spec):
    return definitions_spec['User']


@pytest.fixture
def user_type(user_spec):
    """
    :rtype: User
    """
    return create_model_type('User', user_spec)


@pytest.fixture
def user(user_type):
    """
    :return: instance of a User
    """
    return user_type()


@pytest.fixture
def tag_model(definitions_spec):
    tag_spec = definitions_spec['Tag']
    return create_model_type('Tag', tag_spec)


@pytest.fixture
def pet_spec(definitions_spec):
    return definitions_spec['Pet']
