import mock
import pytest

from swaggerpy.exception import SwaggerError
from swaggerpy import swagger_model
from swaggerpy.swagger_model import (
    validate_required_fields,
)


@pytest.fixture
def context():
    return {}


@pytest.fixture
def required_fields():
    return ['one', 'two']


def test_validate_required_fields_are_present(required_fields, context):
    response = {'one': 1, 'two': 2, 'three': 3}
    validate_required_fields(response, required_fields, context)


def test_validate_required_fields_are_missing(required_fields, context):
    response = {'one': 1, 'three': 3}
    with pytest.raises(SwaggerError) as exc_cm:
        validate_required_fields(response, required_fields, context)

    assert "Missing fields" in str(exc_cm.exconly())


class TestCreateModelType(object):

    model = {
        "id": "Pet",
        "properties": {
            "id": {
                "type": "integer",
                "format": "int64",
                "description": "unique identifier for the pet",
            },
            "category": {
                "$ref": "Category"
            },
            "name": {
                "type": "string"
            },
            "status": {
                "type": "string",
                "description": "pet status in the store",
            }
        },
        'required': ['id', 'category'],
    }

    def test_create_model_type(self):
        model_type = swagger_model.create_model_type(self.model)
        expected = set(['id', 'category', 'name', 'status'])
        instance = model_type(status='ok', id=0, name='')
        assert set(vars(instance)) == expected
        assert set(dir(instance)) == expected
        assert instance == model_type(id=0, name='', status='ok')
        assert model_type._swagger_types == {
            'id': 'integer:int64',
            'category': 'Category',
            'name': 'string',
            'status': 'string',
        }
        assert model_type._required == ['id', 'category']

    @mock.patch('swaggerpy.swagger_model.create_model_docstring', autospec=True)
    def test_create_model_type_lazy_docstring(self, mock_create_docstring):
        model_type = swagger_model.create_model_type(self.model)
        assert not mock_create_docstring.called
        assert model_type.__doc__ == mock_create_docstring.return_value
        mock_create_docstring.assert_called_once_with(self.model['properties'])
