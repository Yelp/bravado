import pytest

from bravado.mapping.docstring import create_param_docstring


def test_param_with_no_default_value(parameter_dict):
    del parameter_dict['default']
    expected = \
        ":param status: the status, yo!\n" \
        ":type status: array\n"
    assert expected == create_param_docstring(parameter_dict)


def test_param_with_default_value(parameter_dict):
    expected = \
        ":param status: the status, yo! (Default: available)\n" \
        ":type status: array\n"
    assert expected == create_param_docstring(parameter_dict)


def test_param_with_no_description(parameter_dict):
    del parameter_dict['description']
    expected = \
        ":param status: Document your spec, yo! (Default: available)\n" \
        ":type status: array\n"
    assert expected == create_param_docstring(parameter_dict)


@pytest.fixture
def parameter_in_body_dict():
    return {
        "in": "body",
        "name": "body",
        "description": "Pet object that needs to be added to the store",
        "required": False,
        "schema": {
            "$ref": "#/definitions/Pet"
        }
    }


def test_param_in_body(parameter_in_body_dict):
    expected = \
        ":param body: Pet object that needs to be added to the store\n" \
        ":type body: #/definitions/Pet\n"
    assert expected == create_param_docstring(parameter_in_body_dict)
