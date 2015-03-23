import unittest

from mock import Mock

from bravado.exception import CancelledError
from bravado.response import HTTPFuture


class HTTPFutureTest(unittest.TestCase):

    def setUp(self):
        self.http_client = Mock()
        self.future = HTTPFuture(self.http_client, None, None)

    def test_raise_cancelled_error_if_result_is_called_after_cancel(self):
        self.future.cancel()
        self.assertRaises(CancelledError, self.future.result)

    def test_cancelled_returns_true_if_called_after_cancel(self):
        self.future.cancel()
        self.assertTrue(self.future.cancelled())
        response = self.http_client.start_request.return_value
        response.cancel.assert_called_once_with()

    def test_cancelled_returns_false_if_called_before_cancel(self):
        self.assertFalse(self.future.cancelled())
