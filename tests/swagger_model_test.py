import pytest

from swaggerpy.exception import SwaggerError
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
