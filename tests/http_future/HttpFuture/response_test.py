# -*- coding: utf-8 -*-
from bravado_core.operation import Operation
from bravado_core.response import IncomingResponse
from mock import Mock

from bravado.exception import BravadoTimeoutError
from bravado.http_future import HttpFuture


def test_fallback_result(mock_future_adapter):
    fallback_result = Mock(name='fallback result')
    mock_future_adapter.result.side_effect = BravadoTimeoutError()

    http_future = HttpFuture(
        future=mock_future_adapter,
        response_adapter=Mock(spec=IncomingResponse),
        operation=Mock(spec=Operation),
    )

    response = http_future.response(fallback_result=lambda e: fallback_result)

    assert response.result == fallback_result
    assert response.response_metadata.is_fallback_result is True
    assert response.response_metadata.exc_info[0] is BravadoTimeoutError
