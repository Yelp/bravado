# -*- coding: utf-8 -*-
import mock

from bravado.response import BravadoResponseMetadata


def test_response_metadata_times():
    with mock.patch('monotonic.monotonic', return_value=11):
        metadata = BravadoResponseMetadata(
            incoming_response=None,
            swagger_result=None,
            start_time=5,
            request_end_time=10,
            handled_exception_info=None,
            request_config=None,
        )

    assert metadata.elapsed_time == 6
    assert metadata.request_elapsed_time == 5
