import pytest

from bravado.mapping.docstring import create_param_docstring


def test_param_with_no_default_value(parameter_spec):
    del parameter_spec['default']
    expected = \
        ":param status: the status, yo! (optional)\n" \
        ":type status: array\n"
    assert expected == create_param_docstring(parameter_spec)


def test_param_with_default_value(parameter_spec):
    expected = \
        ":param status: the status, yo! (Default: available) (optional)\n" \
        ":type status: array\n"
    assert expected == create_param_docstring(parameter_spec)


def test_param_with_no_description(parameter_spec):
    del parameter_spec['description']
    expected = \
        ":param status: Document your spec, yo! (Default: available) (optional)\n" \
        ":type status: array\n"
    assert expected == create_param_docstring(parameter_spec)


def test_param_required_true(parameter_spec):
    parameter_spec['required'] = True
    expected = \
        ":param status: the status, yo! (Default: available)\n" \
        ":type status: array\n"
    assert expected == create_param_docstring(parameter_spec)


def test_param_required_false(parameter_spec):
    parameter_spec['required'] = False
    expected = \
        ":param status: the status, yo! (Default: available) (optional)\n" \
        ":type status: array\n"
    assert expected == create_param_docstring(parameter_spec)


@pytest.fixture
def parameter_in_body_spec():
    return {
        "in": "body",
        "name": "body",
        "description": "Pet object that needs to be added to the store",
        "required": False,
        "schema": {
            "$ref": "#/definitions/Pet"
        }
    }


def test_param_in_body(parameter_in_body_spec):
    expected = \
        ":param body: Pet object that needs to be added to the store (optional)\n" \
        ":type body: #/definitions/Pet\n"
    assert expected == create_param_docstring(parameter_in_body_spec)
