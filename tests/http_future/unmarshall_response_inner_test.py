# -*- coding: utf-8 -*-
import mock
import msgpack
import pytest
from bravado_core.content_type import APP_JSON
from bravado_core.content_type import APP_MSGPACK
from bravado_core.response import IncomingResponse
from bravado_core.spec import Spec

from bravado.http_future import unmarshal_response_inner


@pytest.fixture
def empty_swagger_spec():
    return Spec(spec_dict={})


@pytest.fixture
def response_spec():
    return {
        'description': "Day of the week",
        'schema': {
            'type': 'string',
        }
    }


@pytest.fixture
def mock_get_response_spec():
    with mock.patch('bravado.http_future.get_response_spec') as m:
        yield m


@pytest.fixture
def mock_validate_schema_object():
    with mock.patch('bravado.http_future.validate_schema_object') as m:
        yield m


def test_no_content(mock_get_response_spec, empty_swagger_spec):
    response_spec = {
        'description': "I don't have a 'schema' key so I return nothing",
    }
    response = mock.Mock(spec=IncomingResponse, status_code=200)

    mock_get_response_spec.return_value = response_spec
    op = mock.Mock(swagger_spec=empty_swagger_spec)
    result = unmarshal_response_inner(response, op)
    assert result is None


def test_json_content(mock_get_response_spec, empty_swagger_spec, response_spec):
    response = mock.Mock(
        spec=IncomingResponse,
        status_code=200,
        headers={'content-type': APP_JSON},
        json=mock.Mock(return_value='Monday'),
    )

    mock_get_response_spec.return_value = response_spec
    op = mock.Mock(swagger_spec=empty_swagger_spec)
    assert 'Monday' == unmarshal_response_inner(response, op)


def test_msgpack_content(mock_get_response_spec, empty_swagger_spec, response_spec):
    message = 'Monday'
    response = mock.Mock(
        spec=IncomingResponse,
        status_code=200,
        headers={'content-type': APP_MSGPACK},
        raw_bytes=msgpack.dumps(message),
    )

    mock_get_response_spec.return_value = response_spec
    op = mock.Mock(swagger_spec=empty_swagger_spec)
    assert message == unmarshal_response_inner(response, op)


def test_text_content(mock_get_response_spec, empty_swagger_spec, response_spec):
    response = mock.Mock(
        spec=IncomingResponse,
        status_code=200,
        headers={'content-type': 'text/plain'},
        text='Monday',
    )

    mock_get_response_spec.return_value = response_spec
    op = mock.Mock(swagger_spec=empty_swagger_spec)
    assert 'Monday' == unmarshal_response_inner(response, op)


def test_binary_content(mock_get_response_spec, empty_swagger_spec, response_spec):
    response = mock.Mock(
        spec=IncomingResponse,
        status_code=200,
        headers={'content-type': 'application/octet-stream'},
        text='Monday',
        raw_bytes='SomeBinaryData'
    )

    mock_get_response_spec.return_value = response_spec
    op = mock.Mock(swagger_spec=empty_swagger_spec)
    assert 'SomeBinaryData' == unmarshal_response_inner(response, op)


def test_skips_validation(mock_validate_schema_object, mock_get_response_spec, empty_swagger_spec, response_spec):
    empty_swagger_spec.config['validate_responses'] = False
    response = mock.Mock(
        spec=IncomingResponse,
        status_code=200,
        headers={'content-type': APP_JSON},
        json=mock.Mock(return_value='Monday'),
    )

    mock_get_response_spec.return_value = response_spec
    op = mock.Mock(swagger_spec=empty_swagger_spec)
    unmarshal_response_inner(response, op)
    assert mock_validate_schema_object.call_count == 0


def test_performs_validation(mock_validate_schema_object, mock_get_response_spec, empty_swagger_spec, response_spec):
    empty_swagger_spec.config['validate_responses'] = True
    response = mock.Mock(
        spec=IncomingResponse,
        status_code=200,
        headers={'content-type': APP_JSON},
        json=mock.Mock(return_value='Monday'),
    )

    mock_get_response_spec.return_value = response_spec
    op = mock.Mock(swagger_spec=empty_swagger_spec)
    unmarshal_response_inner(response, op)
    assert mock_validate_schema_object.call_count == 1
