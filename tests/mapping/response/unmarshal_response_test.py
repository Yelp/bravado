from mock import Mock, patch

import pytest

from bravado.mapping.response import ResponseLike, unmarshal_response


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

    with patch('bravado.mapping.response.get_response_spec') as m:
        m.return_value = response_spec
        op = Mock(swagger_spec=empty_swagger_spec)
        result = unmarshal_response(response, op)
        assert (200, None) == result


def test_json_content(empty_swagger_spec, response_spec):
    response = Mock(
        spec=ResponseLike,
        status_code=200,
        json=Mock(return_value='Monday'))

    with patch('bravado.mapping.response.get_response_spec') as m:
        m.return_value = response_spec
        op = Mock(swagger_spec=empty_swagger_spec)
        assert (200, 'Monday') == unmarshal_response(response, op)


def test_skips_validation(empty_swagger_spec, response_spec):
    empty_swagger_spec.config['validate_responses'] = False
    response = Mock(
        spec=ResponseLike,
        status_code=200,
        json=Mock(return_value='Monday'))

    with patch('bravado.mapping.response.validate_schema_object') as val_schem:
        with patch('bravado.mapping.response.get_response_spec') as get_resp:
            get_resp.return_value = response_spec
            op = Mock(swagger_spec=empty_swagger_spec)
            unmarshal_response(response, op)
            assert val_schem.call_count == 0


def test_performs_validation(empty_swagger_spec, response_spec):
    empty_swagger_spec.config['validate_responses'] = True
    response = Mock(
        spec=ResponseLike,
        status_code=200,
        json=Mock(return_value='Monday'))

    with patch('bravado.mapping.response.validate_schema_object') as val_schem:
        with patch('bravado.mapping.response.get_response_spec') as get_resp:
            get_resp.return_value = response_spec
            op = Mock(swagger_spec=empty_swagger_spec)
            unmarshal_response(response, op)
            assert val_schem.call_count == 1
