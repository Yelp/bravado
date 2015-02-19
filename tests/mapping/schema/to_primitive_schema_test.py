from bravado.mapping.schema import to_primitive_schema


def test_integer():
    param_spec = {
        'type': 'integer',
        'name': 'petId',
        'in': 'query',
        'description': 'Unique pet id',
    }
    schema = to_primitive_schema(param_spec)
    expected = param_spec.copy()
    del expected['in']
    assert expected == schema


def test_integer_bells_and_whistles():
    param_spec = {
        'type': 'integer',
        'name': 'petId',
        'in': 'query',
        'description': 'Unique pet id',
        'multipleOf': 5,
        'minimum': 10,
        'maximum': 20,
        'exclusiveMaximum': True,
        'exclusiveMinimum': True,
        'default': 15
    }
    schema = to_primitive_schema(param_spec)
    expected = param_spec.copy()
    del expected['in']
    assert expected == schema


def test_string():
    param_spec = {
        'type': 'string',
        'name': 'username',
        'in': 'query',
        'description': 'Name of the user',
    }
    schema = to_primitive_schema(param_spec)
    expected = param_spec.copy()
    del expected['in']
    assert expected == schema


def test_string_bells_and_whistles():
    param_spec = {
        'type': 'string',
        'name': 'username',
        'in': 'query',
        'description': 'Name of the user',
        'minLength': 5,
        'maxLength': 10,
        'pattern': '[a-z]',
        'format': 'lowercase',
        'default': 'fido'
    }
    schema = to_primitive_schema(param_spec)
    expected = param_spec.copy()
    del expected['in']
    assert expected == schema


def test_boolean():
    param_spec = {
        'type': 'boolean',
        'name': 'has_credit_card',
        'in': 'query',
        'description': 'Does the user have a credit card?',
        'default': False
    }
    schema = to_primitive_schema(param_spec)
    expected = param_spec.copy()
    del expected['in']
    assert expected == schema
