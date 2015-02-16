import pytest

from bravado.mapping.docstring import create_param_docstring


def test_param_with_no_default_value(param_spec):
    del param_spec['default']
    expected = \
        ":param status: the status, yo! (optional)\n" \
        ":type status: array\n"
    assert expected == create_param_docstring(param_spec)


def test_param_with_default_value(param_spec):
    expected = \
        ":param status: the status, yo! (Default: available) (optional)\n" \
        ":type status: array\n"
    assert expected == create_param_docstring(param_spec)


def test_param_with_no_description(param_spec):
    del param_spec['description']
    expected = \
        ":param status: Document your spec, yo! (Default: available) (optional)\n" \
        ":type status: array\n"
    assert expected == create_param_docstring(param_spec)


def test_param_required_true(param_spec):
    param_spec['required'] = True
    expected = \
        ":param status: the status, yo! (Default: available)\n" \
        ":type status: array\n"
    assert expected == create_param_docstring(param_spec)


def test_param_required_false(param_spec):
    param_spec['required'] = False
    expected = \
        ":param status: the status, yo! (Default: available) (optional)\n" \
        ":type status: array\n"
    assert expected == create_param_docstring(param_spec)


@pytest.fixture
def param_in_body_spec():
    return {
        "in": "body",
        "name": "body",
        "description": "Pet object that needs to be added to the store",
        "required": False,
        "schema": {
            "$ref": "#/definitions/Pet"
        }
    }


def test_param_in_body(param_in_body_spec):
    expected = \
        ":param body: Pet object that needs to be added to the store (optional)\n" \
        ":type body: #/definitions/Pet\n"
    assert expected == create_param_docstring(param_in_body_spec)
