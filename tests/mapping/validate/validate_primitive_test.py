from jsonschema.exceptions import ValidationError
import pytest

from bravado.mapping.validate import validate_primitive


@pytest.fixture
def integer_spec():
    return {'type': 'integer'}


@pytest.fixture
def number_spec():
    return {'type': 'number'}


@pytest.fixture
def string_spec():
    return {'type': 'string'}


def test_integer_success(integer_spec):
    validate_primitive(integer_spec, 10)
    validate_primitive(integer_spec, -10)


def test_integer_failure(integer_spec):
    with pytest.raises(ValidationError) as excinfo:
        validate_primitive(integer_spec, 'i am a string')
    assert "is not of type 'integer'" in str(excinfo.value)


def test_integer_multipleOf_success(integer_spec):
    integer_spec['multipleOf'] = 2
    validate_primitive(integer_spec, 10)


def test_integer_multipleOf_failure(integer_spec):
    integer_spec['multipleOf'] = 2
    with pytest.raises(ValidationError) as excinfo:
        validate_primitive(integer_spec, 7)
    assert "not a multiple of" in str(excinfo.value)


def test_integer_maximum_success(integer_spec):
    integer_spec['maximum'] = 10
    validate_primitive(integer_spec, 5)


def test_integer_maximum_failure(integer_spec):
    integer_spec['maximum'] = 10
    with pytest.raises(ValidationError) as excinfo:
        validate_primitive(integer_spec, 11)
    assert "greater than the maximum" in str(excinfo.value)


def test_integer_exclusiveMaximum_success(integer_spec):
    integer_spec['maximum'] = 10
    integer_spec['exclusiveMaximum'] = True
    validate_primitive(integer_spec, 9)


def test_integer_exclusiveMaximum_failure(integer_spec):
    integer_spec['maximum'] = 10
    integer_spec['exclusiveMaximum'] = True
    with pytest.raises(ValidationError) as excinfo:
        validate_primitive(integer_spec, 10)
    assert "greater than or equal to the maximum" in str(excinfo.value)


def test_integer_minimum_success(integer_spec):
    integer_spec['minimum'] = 10
    validate_primitive(integer_spec, 15)


def test_integer_minimum_failure(integer_spec):
    integer_spec['minimum'] = 10
    with pytest.raises(ValidationError) as excinfo:
        validate_primitive(integer_spec, 9)
    assert "less than the minimum" in str(excinfo.value)


def test_integer_exclusiveMinimum_success(integer_spec):
    integer_spec['minimum'] = 10
    integer_spec['exclusiveMinimum'] = True
    validate_primitive(integer_spec, 11)


def test_integer_exclusiveMinimum_failure(integer_spec):
    integer_spec['minimum'] = 10
    integer_spec['exclusiveMinimum'] = True
    with pytest.raises(ValidationError) as excinfo:
        validate_primitive(integer_spec, 10)
    assert "less than or equal to the minimum" in str(excinfo.value)


def test_boolean_success():
    boolean_spec = {
        'type': 'boolean'
    }
    validate_primitive(boolean_spec, True)
    validate_primitive(boolean_spec, False)


def test_boolean_falure():
    boolean_spec = {
        'type': 'boolean'
    }
    with pytest.raises(ValidationError) as excinfo:
        validate_primitive(boolean_spec, "foo")
    assert "is not of type 'boolean'" in str(excinfo.value)


def test_number_success(number_spec):
    validate_primitive(number_spec, 3.14)


def test_number_failure(number_spec):
    with pytest.raises(ValidationError) as excinfo:
        validate_primitive(number_spec, "foo")
    assert "is not of type 'number'" in str(excinfo.value)


def test_number_multipleOf_success(number_spec):
    number_spec['multipleOf'] = 2.3
    validate_primitive(number_spec, 4.6)


def test_number_multipleOf_failure(number_spec):
    number_spec['multipleOf'] = 2.3
    with pytest.raises(ValidationError) as excinfo:
        validate_primitive(number_spec, 9.1)
    assert "not a multiple of" in str(excinfo.value)


def test_string_success(string_spec):
    validate_primitive(string_spec, 'foo')
    validate_primitive(string_spec, u'bar')


def test_string_failure(string_spec):
    with pytest.raises(ValidationError) as excinfo:
        validate_primitive(string_spec, 999)
    assert "is not of type 'string'" in str(excinfo.value)


def test_string_minLength_success(string_spec):
    string_spec['minLength'] = 2
    validate_primitive(string_spec, 'abc')


def test_string_minLength_failure(string_spec):
    string_spec['minLength'] = 3
    with pytest.raises(ValidationError) as excinfo:
        validate_primitive(string_spec, 'ab')
    assert "is too short" in str(excinfo.value)


def test_string_maxLength_success(string_spec):
    string_spec['maxLength'] = 2
    validate_primitive(string_spec, 'ab')


def test_string_maxLength_failure(string_spec):
    string_spec['maxLength'] = 3
    with pytest.raises(ValidationError) as excinfo:
        validate_primitive(string_spec, 'abcdef')
    assert "is too long" in str(excinfo.value)


def test_string_pattern_success(string_spec):
    string_spec['pattern'] = 'foo'
    validate_primitive(string_spec, 'feefiefoofum')


def test_string_pattern_failure(string_spec):
    string_spec['pattern'] = 'foo'
    with pytest.raises(ValidationError) as excinfo:
        validate_primitive(string_spec, 'abcdef')
    assert "does not match" in str(excinfo.value)


def test_string_enum_success(string_spec):
    string_spec['enum'] = ['inky', 'dinky', 'doo']
    validate_primitive(string_spec, 'dinky')


def test_string_enum_failure(string_spec):
    string_spec['enum'] = ['inky', 'dinky', 'doo']
    with pytest.raises(ValidationError) as excinfo:
        validate_primitive(string_spec, 'abc')
    assert "is not one of" in str(excinfo.value)


def test_doesnt_blow_up_when_spec_has_a_require_key():
    string_spec = {
        'type': 'string',
        'require': True,
    }
    validate_primitive(string_spec, 'foo')
