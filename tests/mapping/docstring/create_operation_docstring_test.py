import pytest

from bravado.mapping.docstring import create_operation_docstring
from bravado.mapping.operation import Operation
from bravado.mapping.spec import Spec


@pytest.fixture
def spec():
    return Spec({})


def test_simple(operation_dict, spec):
    expected = \
        "[GET] Finds Pets by status\n\n" \
        "Multiple status values can be provided with comma seperated strings\n\n" \
        ":param status: the status, yo! (Default: available)\n" \
        ":type status: array\n" \
        ":returns: 200: successful operation\n" \
        ":rtype: array:#/definitions/Pet\n" \
        ":returns: 400: Invalid status value\n"

    operation = Operation(spec, '/pet', 'get', operation_dict)
    assert expected == create_operation_docstring(operation)


def test_no_parameters(operation_dict, spec):
    del operation_dict['parameters']
    expected = \
        "[GET] Finds Pets by status\n\n" \
        "Multiple status values can be provided with comma seperated strings\n\n" \
        ":returns: 200: successful operation\n" \
        ":rtype: array:#/definitions/Pet\n" \
        ":returns: 400: Invalid status value\n"

    operation = Operation(spec, '/pet', 'get', operation_dict)
    assert expected == create_operation_docstring(operation)


def test_deprecated(operation_dict, spec):
    expected = \
        "** DEPRECATED **\n" \
        "[GET] Finds Pets by status\n\n" \
        "Multiple status values can be provided with comma seperated strings\n\n" \
        ":param status: the status, yo! (Default: available)\n" \
        ":type status: array\n" \
        ":returns: 200: successful operation\n" \
        ":rtype: array:#/definitions/Pet\n" \
        ":returns: 400: Invalid status value\n"

    operation_dict['deprecated'] = True
    operation = Operation(spec, '/pet', 'get', operation_dict)
    assert expected == create_operation_docstring(operation)


def test_no_summary(operation_dict, spec):
    expected = \
        "Multiple status values can be provided with comma seperated strings\n\n" \
        ":param status: the status, yo! (Default: available)\n" \
        ":type status: array\n" \
        ":returns: 200: successful operation\n" \
        ":rtype: array:#/definitions/Pet\n" \
        ":returns: 400: Invalid status value\n"

    del operation_dict['summary']
    operation = Operation(spec, '/pet', 'get', operation_dict)
    assert expected == create_operation_docstring(operation)


def test_no_description(operation_dict, spec):
    expected = \
        "[GET] Finds Pets by status\n\n" \
        ":param status: the status, yo! (Default: available)\n" \
        ":type status: array\n" \
        ":returns: 200: successful operation\n" \
        ":rtype: array:#/definitions/Pet\n" \
        ":returns: 400: Invalid status value\n"

    del operation_dict['description']
    operation = Operation(spec, '/pet', 'get', operation_dict)
    assert expected == create_operation_docstring(operation)
