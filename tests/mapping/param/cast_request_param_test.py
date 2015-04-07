from bravado.mapping.param import cast_request_param


def test_integer():
    assert 34 == cast_request_param('integer', 'biz_id', '34')


def test_boolean():
    assert cast_request_param('boolean', 'is_open', 1)
    assert not cast_request_param('boolean', 'is_open', 0)


def test_number():
    assert 2.34 == cast_request_param('number', 'score', '2.34')


def test_unknown_type_returns_untouched_value():
    assert 'abc123' == cast_request_param('unknown_type', 'blah', 'abc123')


def test_none_returns_none():
    assert cast_request_param('integer', 'biz_id', None) is None
