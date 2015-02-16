import pytest

from bravado.mapping.docstring import create_operation_docstring
from bravado.mapping.operation import Operation
from bravado.mapping.spec import Spec


def test_simple(op_spec, empty_swagger_spec):
    expected = \
        "[GET] Finds Pets by status\n\n" \
        "Multiple status values can be provided with comma seperated strings\n\n" \
        ":param status: the status, yo! (Default: available) (optional)\n" \
        ":type status: array\n" \
        ":returns: 200: successful operation\n" \
        ":rtype: array:#/definitions/Pet\n" \
        ":returns: 400: Invalid status value\n"

    op = Operation(empty_swagger_spec, '/pet', 'get', op_spec)
    assert expected == create_operation_docstring(op)


def test_no_parameters(op_spec, empty_swagger_spec):
    del op_spec['parameters']
    expected = \
        "[GET] Finds Pets by status\n\n" \
        "Multiple status values can be provided with comma seperated strings\n\n" \
        ":returns: 200: successful operation\n" \
        ":rtype: array:#/definitions/Pet\n" \
        ":returns: 400: Invalid status value\n"

    op = Operation(empty_swagger_spec, '/pet', 'get', op_spec)
    assert expected == create_operation_docstring(op)


def test_deprecated(op_spec, empty_swagger_spec):
    expected = \
        "** DEPRECATED **\n" \
        "[GET] Finds Pets by status\n\n" \
        "Multiple status values can be provided with comma seperated strings\n\n" \
        ":param status: the status, yo! (Default: available) (optional)\n" \
        ":type status: array\n" \
        ":returns: 200: successful operation\n" \
        ":rtype: array:#/definitions/Pet\n" \
        ":returns: 400: Invalid status value\n"

    op_spec['deprecated'] = True
    op = Operation(empty_swagger_spec, '/pet', 'get', op_spec)
    assert expected == create_operation_docstring(op)


def test_no_summary(op_spec, empty_swagger_spec):
    expected = \
        "Multiple status values can be provided with comma seperated strings\n\n" \
        ":param status: the status, yo! (Default: available) (optional)\n" \
        ":type status: array\n" \
        ":returns: 200: successful operation\n" \
        ":rtype: array:#/definitions/Pet\n" \
        ":returns: 400: Invalid status value\n"

    del op_spec['summary']
    op= Operation(empty_swagger_spec, '/pet', 'get', op_spec)
    assert expected == create_operation_docstring(op)


def test_no_description(op_spec, empty_swagger_spec):
    expected = \
        "[GET] Finds Pets by status\n\n" \
        ":param status: the status, yo! (Default: available) (optional)\n" \
        ":type status: array\n" \
        ":returns: 200: successful operation\n" \
        ":rtype: array:#/definitions/Pet\n" \
        ":returns: 400: Invalid status value\n"

    del op_spec['description']
    op = Operation(empty_swagger_spec, '/pet', 'get', op_spec)
    assert expected == create_operation_docstring(op)
