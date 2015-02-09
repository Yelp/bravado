import pytest

from bravado.mapping.docstring import create_operation_docstring
from bravado.mapping.operation import Operation
from bravado.mapping.spec import Spec


@pytest.fixture
def root_spec():
    return Spec({})


def test_simple(operation_spec, root_spec):
    expected = \
        "[GET] Finds Pets by status\n\n" \
        "Multiple status values can be provided with comma seperated strings\n\n" \
        ":param status: the status, yo! (Default: available) (optional)\n" \
        ":type status: array\n" \
        ":returns: 200: successful operation\n" \
        ":rtype: array:#/definitions/Pet\n" \
        ":returns: 400: Invalid status value\n"

    operation = Operation(root_spec, '/pet', 'get', operation_spec)
    assert expected == create_operation_docstring(operation)


def test_no_parameters(operation_spec, root_spec):
    del operation_spec['parameters']
    expected = \
        "[GET] Finds Pets by status\n\n" \
        "Multiple status values can be provided with comma seperated strings\n\n" \
        ":returns: 200: successful operation\n" \
        ":rtype: array:#/definitions/Pet\n" \
        ":returns: 400: Invalid status value\n"

    operation = Operation(root_spec, '/pet', 'get', operation_spec)
    assert expected == create_operation_docstring(operation)


def test_deprecated(operation_spec, root_spec):
    expected = \
        "** DEPRECATED **\n" \
        "[GET] Finds Pets by status\n\n" \
        "Multiple status values can be provided with comma seperated strings\n\n" \
        ":param status: the status, yo! (Default: available) (optional)\n" \
        ":type status: array\n" \
        ":returns: 200: successful operation\n" \
        ":rtype: array:#/definitions/Pet\n" \
        ":returns: 400: Invalid status value\n"

    operation_spec['deprecated'] = True
    operation = Operation(root_spec, '/pet', 'get', operation_spec)
    assert expected == create_operation_docstring(operation)


def test_no_summary(operation_spec, root_spec):
    expected = \
        "Multiple status values can be provided with comma seperated strings\n\n" \
        ":param status: the status, yo! (Default: available) (optional)\n" \
        ":type status: array\n" \
        ":returns: 200: successful operation\n" \
        ":rtype: array:#/definitions/Pet\n" \
        ":returns: 400: Invalid status value\n"

    del operation_spec['summary']
    operation = Operation(root_spec, '/pet', 'get', operation_spec)
    assert expected == create_operation_docstring(operation)


def test_no_description(operation_spec, root_spec):
    expected = \
        "[GET] Finds Pets by status\n\n" \
        ":param status: the status, yo! (Default: available) (optional)\n" \
        ":type status: array\n" \
        ":returns: 200: successful operation\n" \
        ":rtype: array:#/definitions/Pet\n" \
        ":returns: 400: Invalid status value\n"

    del operation_spec['description']
    operation = Operation(root_spec, '/pet', 'get', operation_spec)
    assert expected == create_operation_docstring(operation)
