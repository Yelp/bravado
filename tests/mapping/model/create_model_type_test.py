import mock

from bravado.mapping.model import create_model_type
from tests.mapping.model.conftest import pet_dict as pet_dict_fixture
from tests.mapping.model.conftest import \
    definitions_dict as definitions_dict_fixture


def test_pet_model(pet_dict):
    model_type = create_model_type('Pet', pet_dict)
    expected = set(['id', 'category', 'name', 'photoUrls', 'tags'])
    instance = model_type(id=1, name='Darwin')
    assert set(vars(instance).keys()) == expected
    assert set(dir(instance)) == expected
    assert instance == model_type(id=1, name='Darwin')
    assert model_type._swagger_types == {
        'id': 'integer:int64',
        'category': '#/definitions/Category',
        'name': 'string',
        'photoUrls': 'array:string',
        'tags': 'array:#/definitions/Tag'
    }
    assert model_type._required == ['name', 'photoUrls']


@mock.patch('bravado.mapping.model.create_model_docstring', autospec=True)
def test_create_model_type_lazy_docstring(mock_create_docstring):
    # NOTE: some sort of weird interaction with pytest, pytest-mock and mock
    #       made using the 'mocker' fixture here a no-go.
    definitions_dict = definitions_dict_fixture()
    pet_dict = pet_dict_fixture(definitions_dict)
    pet_type = create_model_type('Pet', pet_dict)
    assert not mock_create_docstring.called
    assert pet_type.__doc__ == mock_create_docstring.return_value
    mock_create_docstring.assert_called_once_with(pet_dict['properties'])