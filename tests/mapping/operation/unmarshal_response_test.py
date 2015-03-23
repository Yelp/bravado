from mock import Mock, patch

from bravado.mapping.operation import unmarshal_response
from bravado.mapping.response import ResponseLike


def test_no_content(empty_swagger_spec):
    response_spec = {
        'description': "I don't have a 'schema' key so I return nothing",
    }
    response = Mock(spec=ResponseLike, status_code=200)
    with patch('bravado.mapping.operation.get_response_spec') as m:
        m.return_value = response_spec
        op = Mock(swagger_spec=empty_swagger_spec)
        status_code, value = unmarshal_response(response, op)
    assert 200 == status_code
    assert value is None


def test_json_content(empty_swagger_spec):
    response_spec = {
        'description': "Day of the week",
        'schema': {
            'type': 'string',
        }
    }
    op = Mock(swagger_spec=empty_swagger_spec)
    response = Mock(
        spec=ResponseLike,
        status_code=200,
        json=Mock(return_value='Monday'))

    with patch('bravado.mapping.operation.get_response_spec') as m:
        m.return_value = response_spec
        op = Mock(swagger_spec=empty_swagger_spec)
        status_code, value = unmarshal_response(response, op)
    assert 200 == status_code
    assert 'Monday' == value
