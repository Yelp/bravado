import pytest

from bravado.mapping.schema import to_array_schema


@pytest.fixture
def param_spec():
    return {
        'name': 'status',
        'in': 'query',
        'description': 'Status values that need to be considered for filter',
        'required': False,
        'type': 'array',
        'items': {
            'type': 'string',
         },
        'collectionFormat': 'multi',
        'default': 'available'
    }


def test_array_of_string(param_spec):
    schema = to_array_schema(param_spec)
    expected = param_spec.copy()
    del expected['in']
    del expected['required']
    del expected['collectionFormat']
    del expected['default']
    assert expected == schema


def test_nested_array_of_string(param_spec):
    words_lists_spec = {
        'name': 'words_lists',
        'in': 'query',
        'description': 'list of list of words',
        'required': False,
        'type': 'array',
        'minLength': 1,
        'items': {
            'name': 'words',
            'description': 'list of words',
            'type': 'array',
            'maxLength': 10,
            'default': 'boo',
            'items': {
                'type': 'string',
                'maxLength': 10
            },
         },
        'collectionFormat': 'multi',
    }
    schema = to_array_schema(words_lists_spec)
    expected = {
        'name': 'words_lists',
        'description': 'list of list of words',
        'type': 'array',
        'items': {
            'name': 'words',
            'description': 'list of words',
            'type': 'array',
            'items': {
                'type': 'string',
                'maxLength': 10
            },
        },
    }
    assert expected == schema
