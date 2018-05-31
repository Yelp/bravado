# -*- coding: utf-8 -*-
import mock

from bravado.response import BravadoResponseMetadata
from bravado.response import get_metadata_class


class ResponseMetadata(object):
    pass


def test_get_metadata_class_invalid_str():
    with mock.patch('bravado.config.log') as mock_log:
        metadata_class = get_metadata_class('some_invalid_str')
    assert metadata_class is BravadoResponseMetadata
    assert mock_log.warning.call_count == 1


def test_get_metadata_class_invalid_class():
    with mock.patch('bravado.response.log') as mock_log:
        metadata_class = get_metadata_class('tests.response_test.ResponseMetadata')
    assert metadata_class is BravadoResponseMetadata
    assert mock_log.warning.call_count == 1
