# -*- coding: utf-8 -*-

import mock

import swaggerpy.multipart_response

from swaggerpy.http_client import MULT_FORM
from swaggerpy.multipart_response import add_lines
from swaggerpy.multipart_response import create_multipart_content


def test_add_lines_string():
    name = 'param1'
    content = 'value1'
    is_file = False
    boundary = 'boundary'
    lines = []

    lines = add_lines(name, content, is_file, boundary, lines)

    assert lines == [
        "--boundary",
        "Content-Disposition: form-data; name=param1",
        "",
        "value1"
    ]


def test_add_lines_int():
    name = 'param1'
    content = 13
    is_file = False
    boundary = 'boundary'
    lines = []

    lines = add_lines(name, content, is_file, boundary, lines)

    assert lines == [
        "--boundary",
        "Content-Disposition: form-data; name=param1",
        "",
        "13"
    ]


def test_add_lines_file():
    name = 'param1'
    content = '\x80\xff\x80'
    is_file = True
    boundary = 'boundary'
    lines = []

    lines = add_lines(name, content, is_file, boundary, lines)

    assert lines == [
        "--boundary",
        "Content-Disposition: form-data; name=param1; filename=param1",
        "",
        "\x80\xff\x80"
    ]


def test_create_multipart_content():
    boundary = '**********'
    headers = {}
    request_params = {
        'data': {
            'string_data': 'something',
            'number_data': 13,
        },
        'files': {
            'filename.txt': mock.Mock(read=mock.Mock(return_value='\x80\xff\x80')),
        }
    }

    expected_headers = {'content-type': MULT_FORM + "; boundary=**********"}
    expected_response = '--**********\r\nContent-Disposition: form-data; name=string_data\r\n\r\nsomething\r\n--**********\r\nContent-Disposition: form-data; name=number_data\r\n\r\n13\r\n--**********\r\nContent-Disposition: form-data; name=filename.txt; filename=filename.txt\r\n\r\n\x80\xff\x80\r\n--**********--\r\n'

    with mock.patch('swaggerpy.multipart_response.get_random_boundary', return_value=boundary):
        assert create_multipart_content(request_params, headers) == expected_response
        assert headers == expected_headers
