from mock import Mock, patch

import pytest

from bravado.mapping.operation import unmarshal_response
from bravado.mapping.response import ResponseLike


@pytest.fixture
def response_spec():
    return {
        'description': "Day of the week",
        'schema': {
            'type': 'string',
        }
    }


def test_no_content(empty_swagger_spec):
    response_spec = {
        'description': "I don't have a 'schema' key so I return nothing",
    }
    response = Mock(spec=ResponseLike, status_code=200)

    with patch('bravado.mapping.operation.get_response_spec') as m:
        m.return_value = response_spec
        op = Mock(swagger_spec=empty_swagger_spec)
        result = unmarshal_response(response, op)
        assert (200, None) == result


def test_json_content(empty_swagger_spec, response_spec):
    response = Mock(
        spec=ResponseLike,
        status_code=200,
        json=Mock(return_value='Monday'))

    with patch('bravado.mapping.operation.get_response_spec') as m:
        m.return_value = response_spec
        op = Mock(swagger_spec=empty_swagger_spec)
        assert (200, 'Monday') == unmarshal_response(response, op)


def test_skips_validation(empty_swagger_spec, response_spec):
    empty_swagger_spec.config['validate_responses'] = False
    response = Mock(
        spec=ResponseLike,
        status_code=200,
        json=Mock(return_value='Monday'))

    with patch('bravado.mapping.operation.validate_schema_object') as m1:
        with patch('bravado.mapping.operation.get_response_spec') as m:
            m.return_value = response_spec
            op = Mock(swagger_spec=empty_swagger_spec)
            unmarshal_response(response, op)
            assert m1.call_count == 0


def test_performs_validation(empty_swagger_spec, response_spec):
    empty_swagger_spec.config['validate_responses'] = True
    response = Mock(
        spec=ResponseLike,
        status_code=200,
        json=Mock(return_value='Monday'))

    with patch('bravado.mapping.operation.validate_schema_object') as m1:
        with patch('bravado.mapping.operation.get_response_spec') as m:
            m.return_value = response_spec
            op = Mock(swagger_spec=empty_swagger_spec)
            unmarshal_response(response, op)
            assert m1.call_count == 1
