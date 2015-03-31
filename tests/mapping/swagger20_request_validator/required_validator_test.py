import mock

from jsonschema.exceptions import ValidationError

from bravado.mapping.swagger20_validator import required_validator


def test_fail_if_required_parameter_but_not_present():
    param_schema = {'name': 'foo', 'in': 'query', 'required': True}
    assert isinstance(required_validator(
        None, param_schema['required'], None, param_schema)[0],
        ValidationError)


def test_pass_if_not_required_paramter_and_not_present():
    param_schema = {'name': 'foo', 'in': 'query', 'required': False}
    assert required_validator(
        None, param_schema['required'], None, param_schema) is None


def test_call_to_jsonschema_if_not_param():
    param_schema = {'name': 'foo', 'required': True}
    with mock.patch('jsonschema._validators.required_draft4') as m:
        required_validator('a', 'b', 'c', param_schema)
    m.assert_called_once_with('a', 'b', 'c', param_schema)
