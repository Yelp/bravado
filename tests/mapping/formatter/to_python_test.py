from datetime import date, datetime

from bravado.mapping.formatter import to_python


def test_date():
    spec = {'type': 'string', 'format': 'date'}
    assert date(2015, 4, 1) == to_python('2015-04-01', spec)


def test_datetime():
    spec = {'type': 'string', 'format': 'date-time'}
    result = to_python('2015-03-22T13:19:54', spec)
    assert datetime(2015, 3, 22, 13, 19, 54) == result


def test_int64_long():
    spec = {'type': 'integer', 'format': 'int64'}
    result = to_python(999L, spec)
    assert 999L == result


def test_int64_int():
    spec = {'type': 'integer', 'format': 'int64'}
    result = to_python(int(999), spec)
    assert 999L == result
    assert isinstance(result, long)


def test_int32_long():
    spec = {'type': 'integer', 'format': 'int32'}
    result = to_python(999L, spec)
    assert 999 == result
    assert isinstance(result, int)


def test_int32_int():
    spec = {'type': 'integer', 'format': 'int32'}
    result = to_python(999, spec)
    assert 999L == result
    assert isinstance(result, int)


def test_float():
    spec = {'type': 'number', 'format': 'float'}
    result = to_python(float(3.14), spec)
    assert 3.14 == result
    assert isinstance(result, float)


def test_double():
    spec = {'type': 'number', 'format': 'double'}
    result = to_python(float(3.14), spec)
    assert 3.14 == result
    assert isinstance(result, float)


def test_byte():
    spec = {'type': 'string', 'format': 'byte'}
    result = to_python('x', spec)
    assert 'x' == result
    assert isinstance(result, str)
