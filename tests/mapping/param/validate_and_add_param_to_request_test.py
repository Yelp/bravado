from mock import Mock, patch
import pytest

from bravado.mapping.param import validate_and_add_params_to_request
from bravado.mapping.spec import Spec


@pytest.fixture
def empty_swagger_spec():
    return Spec({})


@pytest.fixture
def mock_request():
    return Mock('requests.Request', autospec=True)


@pytest.fixture
def param_spec():
    return {
        'name': 'test_bool_param',
        'type': 'boolean',
        'in': 'query',
        'required': True,
    }


def test_unrequired_param_not_added_to_request_when_none(
        empty_swagger_spec, param_spec, mock_request):
    param_spec['required'] = False

    with patch('bravado.mapping.param.add_param_to_req') as mock_add_param:
        validate_and_add_params_to_request(
            empty_swagger_spec, param_spec, None, mock_request)
        assert not mock_add_param.called


def test_required_param_added_to_request_when_not_none(
        empty_swagger_spec, param_spec, mock_request):
    param_spec['required'] = True

    with patch('bravado.mapping.param.add_param_to_req') as mock_add_param:
        validate_and_add_params_to_request(
            empty_swagger_spec, param_spec, True, mock_request)
        assert mock_add_param.called


def test_required_param_raises_error_when_none(
        empty_swagger_spec, param_spec, mock_request):

    with pytest.raises(TypeError) as excinfo:
        validate_and_add_params_to_request(
            empty_swagger_spec, param_spec, None, mock_request)
    assert 'should be in types' in str(excinfo.value)
