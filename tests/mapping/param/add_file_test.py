from bravado.mapping.exception import SwaggerMappingError
from mock import Mock
import pytest

from bravado.mapping.operation import Operation
from bravado.mapping.param import add_file, Param


def test_single_file(empty_swagger_spec):
    request = {}
    file_contents = "I am the contents of a file"
    op = Mock(spec=Operation, consumes=['multipart/form-data'])
    param_spec = {
        'type': 'file',
        'in': 'formData',
        'name': 'photo'
    }
    param = Param(empty_swagger_spec, op, param_spec)
    add_file(param, file_contents, request)
    expected_request = {
        'file': [('files', ('photo', 'I am the contents of a file'))]
    }
    assert expected_request == request


def test_multiple_files(empty_swagger_spec):
    request = {}
    file1_contents = "I am the contents of a file1"
    file2_contents = "I am the contents of a file2"
    op = Mock(spec=Operation, consumes=['multipart/form-data'])
    param1_spec = {
        'type': 'file',
        'in': 'formData',
        'name': 'photo'
    }
    param2_spec = {
        'type': 'file',
        'in': 'formData',
        'name': 'headshot'
    }

    param1 = Param(empty_swagger_spec, op, param1_spec)
    param2 = Param(empty_swagger_spec, op, param2_spec)
    add_file(param1, file1_contents, request)
    add_file(param2, file2_contents, request)
    expected_request = {
        'file': [
            ('files', ('photo', 'I am the contents of a file1')),
            ('files', ('headshot', 'I am the contents of a file2')),
        ]
    }
    assert expected_request == request


def test_mime_type_not_found_in_consumes(empty_swagger_spec):
    request = {}
    file_contents = "I am the contents of a file"
    op = Mock(spec=Operation, operation_id='upload_photos', consumes=[])
    param_spec = {
        'type': 'file',
        'in': 'formData',
        'name': 'photo'
    }
    param = Param(empty_swagger_spec, op, param_spec)
    with pytest.raises(SwaggerMappingError) as excinfo:
        add_file(param, file_contents, request)
    assert "not found in list of supported mime-types" in str(excinfo.value)
