from bravado.mapping.operation import Operation
from bravado.mapping.spec import Spec


def test_returns_consumes_from_op(minimal_swagger_dict):
    op_spec = {
        'consumes': ['multipart/form-data']
    }
    minimal_swagger_spec = Spec.from_dict(minimal_swagger_dict)
    op = Operation(minimal_swagger_spec, '/foo', 'get', op_spec)
    assert ['multipart/form-data'] == op.consumes


def test_returns_consumes_from_swagger_spec_when_not_present_on_op(
        minimal_swagger_dict):
    op_spec = {
        # 'consumes' left out intentionally
    }
    minimal_swagger_dict['consumes'] = ['multipart/form-data']
    minimal_swagger_spec = Spec.from_dict(minimal_swagger_dict)
    op = Operation(minimal_swagger_spec, '/foo', 'get', op_spec)
    assert ['multipart/form-data'] == op.consumes


def test_consumes_on_op_overrides_consumes_from_swagger_spec(
        minimal_swagger_dict):
    op_spec = {
        'consumes': ['application/x-www-form-urlencoded']
    }
    minimal_swagger_dict['consumes'] = ['multipart/form-data']
    minimal_swagger_spec = Spec.from_dict(minimal_swagger_dict)
    op = Operation(minimal_swagger_spec, '/foo', 'get', op_spec)
    assert ['application/x-www-form-urlencoded'] == op.consumes


def test_consumes_not_present_on_swagger_spec_returns_empty_array(
        minimal_swagger_dict):
    # The point being, None should never be returned
    op_spec = {
        # 'consumes' left out intentionally
    }
    minimal_swagger_spec = Spec.from_dict(minimal_swagger_dict)
    op = Operation(minimal_swagger_spec, '/foo', 'get', op_spec)
    assert [] == op.consumes
