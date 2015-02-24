import mock

from bravado.mapping.model import create_model_type
from tests.mapping.model.conftest import pet_spec as pet_spec_fixture
from tests.mapping.model.conftest import \
    definitions_spec as definitions_spec_fixture


def test_pet_model(pet_spec):
    Pet = create_model_type('Pet', pet_spec)
    expected = set(['id', 'category', 'name', 'photoUrls', 'tags'])
    pet = Pet(id=1, name='Darwin')
    assert set(vars(pet).keys()) == expected
    assert set(dir(pet)) == expected
    assert pet == Pet(id=1, name='Darwin')
    assert pet != Pet(id=2, name='Fido')
    assert Pet._swagger_types == {
        'id': 'integer:int64',
        'category': '#/definitions/Category',
        'name': 'string',
        'photoUrls': 'array:string',
        'tags': 'array:#/definitions/Tag'
    }
    assert Pet._required == ['name', 'photoUrls']


def test_no_arg_constructor(pet_spec):
    Pet = create_model_type('Pet', pet_spec)
    attr_names = (
        #'__doc__',  <-- will trigger docstring generation so skip for now
        '__eq__',
        '__init__',
        '__repr__',
        '__dir__',
        '_flat_dict',
        '_swagger_types',
        '_required',
    )
    for attr_name in attr_names:
        assert hasattr(Pet, attr_name)


@mock.patch('bravado.mapping.model.create_model_docstring', autospec=True)
def test_create_model_type_lazy_docstring(mock_create_docstring):
    # NOTE: some sort of weird interaction with pytest, pytest-mock and mock
    #       made using the 'mocker' fixture here a no-go.
    definitions_spec = definitions_spec_fixture()
    pet_spec = pet_spec_fixture(definitions_spec)
    pet_type = create_model_type('Pet', pet_spec)
    assert not mock_create_docstring.called
    assert pet_type.__doc__ == mock_create_docstring.return_value
    mock_create_docstring.assert_called_once_with(pet_spec)


# ################################################################
# # Test that bravado correctly creates model_dict
# # classes from swagger model_dict definitions
# # API calls are not triggered here.
# # Scope is limited to model_dict model in swagger api spec
# ################################################################
#
# @httpretty.activate
# def test_nones_for_dates_on_model_types_creation(self):
#     # TODO: move to create_model_type_test.py
#     self.models['User']['properties']['date'] = {
#         'type': 'string',
#         'format': 'date'}
#     self.models['User']['properties']['datetime'] = {
#         'type': 'string',
#         'format': 'date-time'}
#     self.register_urls()
#     resource = SwaggerClient.from_url(
#         u'http://localhost/api-docs').api_test
#     User = resource.testHTTP._models['User']
#     self.assertEqual(
#         {"schools": [], "id": 0L, "date": None, "datetime": None},
#         User().__dict__
#     )
#
