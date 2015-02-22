from mock import Mock

from bravado.mapping.operation import unmarshal_response
from bravado.mapping.response import ResponseLike


def test_no_content(empty_swagger_spec):
    response_spec = {
        'description': "I don't have a 'schema' key so I return nothing",
    }
    response = Mock(spec=ResponseLike, status_code=200)
    status_code, value = unmarshal_response(
        empty_swagger_spec, response_spec, response)
    assert 200 == status_code
    assert value is None


def test_json_content(empty_swagger_spec):
    response_spec = {
        'description': "Day of the week",
        'schema': {
            'type': 'string',
        }
    }
    response = Mock(
        spec=ResponseLike,
        status_code=200,
        json=Mock(return_value='Monday'))

    status_code, value = unmarshal_response(
        empty_swagger_spec, response_spec, response)
    assert 200 == status_code
    assert 'Monday' == value
