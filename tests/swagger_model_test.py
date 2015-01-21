
import mock

from bravado import swagger_model


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
        instance = model_type(status='ok')
        assert set(vars(instance).keys()) == expected
        assert set(dir(instance)) == expected
        assert instance == model_type(id=0, name='', status='ok')
        assert model_type._swagger_types == {
            'id': 'integer:int64',
            'category': 'Category',
            'name': 'string',
            'status': 'string',
        }
        assert model_type._required == ['id', 'category']

    @mock.patch('bravado.swagger_model.create_model_docstring', autospec=True)
    def test_create_model_type_lazy_docstring(self, mock_create_docstring):
        model_type = swagger_model.create_model_type(self.model)
        assert not mock_create_docstring.called
        assert model_type.__doc__ == mock_create_docstring.return_value
        mock_create_docstring.assert_called_once_with(self.model['properties'])
