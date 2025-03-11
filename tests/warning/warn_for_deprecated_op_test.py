# -*- coding: utf-8 -*-
try:
    from unittest.mock import Mock, patch
except ImportError:
    from mock import Mock, patch

from bravado.client import CallableOperation
from bravado.warning import warn_for_deprecated_op


@patch('bravado.warning.warnings.warn')
def test_warn(mock_warn):
    op_spec = {'deprecated': True,
               'x-deprecated-date': 'foo',
               'x-removal-date': 'bar'}
    op = Mock(spec=CallableOperation, operation_id='bla', op_spec=op_spec)
    warn_for_deprecated_op(op)
    mock_warn.assert_called_once_with(
        '[DEPRECATED] bla has now been deprecated.'
        ' Deprecation Date: foo. Removal Date: bar', Warning)


@patch('bravado.warning.warnings.warn')
def test_no_warn_if_false(mock_warn):
    op_spec = {'deprecated': False}
    op = Mock(spec=CallableOperation, operation_id='bla', op_spec=op_spec)
    warn_for_deprecated_op(op)
    assert not mock_warn.called


@patch('bravado.warning.warnings.warn')
def test_no_warn_if_deprecate_flag_not_present(mock_warn):
    op = Mock(spec=CallableOperation, operation_id='bla', op_spec={})
    warn_for_deprecated_op(op)
    assert not mock_warn.called
