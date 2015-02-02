from mock import Mock, patch
import pytest

from bravado.mapping.param import validate_and_add_params_to_request
from bravado.mapping.spec import Spec


@pytest.fixture
def spec():
    return Spec({})


@pytest.fixture
def mock_request():
    return Mock('requests.Request', autospec=True)


@pytest.fixture
def param_dict():
    return {
        'name': 'test_bool_param',
        'type': 'boolean',
        'in': 'query',
        'required': True,
    }


def test_unrequired_param_not_added_to_request_when_none(
        spec, param_dict, mock_request):
    param_dict['required'] = False

    with patch('bravado.mapping.param.add_param_to_req') as mock_add_param:
        validate_and_add_params_to_request(spec, param_dict, None, mock_request)
        assert not mock_add_param.called


def test_required_param_added_to_request_when_not_none(
        spec, param_dict, mock_request):
    param_dict['required'] = True

    with patch('bravado.mapping.param.add_param_to_req') as mock_add_param:
        validate_and_add_params_to_request(spec, param_dict, True, mock_request)
        assert mock_add_param.called


def test_required_param_raises_error_when_none(spec, param_dict, mock_request):
    with pytest.raises(TypeError) as excinfo:
        validate_and_add_params_to_request(spec, param_dict, None, mock_request)
    assert 'should be in types' in str(excinfo.value)
