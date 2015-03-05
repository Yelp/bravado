from datetime import date, datetime

from bravado.mapping.formatter import to_python


def test_none():
    spec = {'type': 'string', 'format': 'date'}
    assert to_python(spec, None) is None


def test_no_format_returns_value():
    spec = {'type': 'string'}
    assert 'boo' == to_python(spec, 'boo')


def test_date():
    spec = {'type': 'string', 'format': 'date'}
    assert date(2015, 4, 1) == to_python(spec, '2015-04-01')


def test_datetime():
    spec = {'type': 'string', 'format': 'date-time'}
    result = to_python(spec, '2015-03-22T13:19:54')
    assert datetime(2015, 3, 22, 13, 19, 54) == result


def test_int64_long():
    spec = {'type': 'integer', 'format': 'int64'}
    result = to_python(spec, 999L)
    assert 999L == result


def test_int64_int():
    spec = {'type': 'integer', 'format': 'int64'}
    result = to_python(spec, 999)
    assert 999L == result
    assert isinstance(result, long)


def test_int32_long():
    spec = {'type': 'integer', 'format': 'int32'}
    result = to_python(spec, 999L)
    assert 999 == result
    assert isinstance(result, int)


def test_int32_int():
    spec = {'type': 'integer', 'format': 'int32'}
    result = to_python(spec, 999)
    assert 999 == result
    assert isinstance(result, int)


def test_float():
    spec = {'type': 'number', 'format': 'float'}
    result = to_python(spec, float(3.14))
    assert 3.14 == result
    assert isinstance(result, float)


def test_double():
    spec = {'type': 'number', 'format': 'double'}
    result = to_python(spec, float(3.14))
    assert 3.14 == result
    assert isinstance(result, float)


def test_byte():
    spec = {'type': 'string', 'format': 'byte'}
    result = to_python(spec, 'x')
    assert 'x' == result
    assert isinstance(result, str)
