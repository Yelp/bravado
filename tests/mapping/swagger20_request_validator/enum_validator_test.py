import mock

from bravado.mapping.swagger20_validator import enum_validator


def test_multiple_jsonschem_call_if_enum_items_present_as_array():
    enums = ['a1', 'b2', 'c3']
    param_schema = {
        'name': 'foo',
        'in': 'query',
        'type': 'array',
        'items': {'type': 'array'},
        'enum': enums
        }
    with mock.patch('jsonschema._validators.enum') as m:
        [list(x) for x in enum_validator(
            None, enums, ['a1', 'd4'], param_schema)]
    m.assert_any_call(None, enums, 'a1', param_schema)
    m.assert_any_call(None, enums, 'd4', param_schema)


def test_single_jsonschema_call_if_enum_instance_not_array():
    enums = ['a1', 'b2', 'c3']
    param_schema = {
        'enum': enums
        }
    with mock.patch('jsonschema._validators.enum') as m:
        [list(x) for x in enum_validator(
            None, enums, ['a1', 'd4'], param_schema)]
    m.assert_called_once_with(None, enums, ['a1', 'd4'], param_schema)
