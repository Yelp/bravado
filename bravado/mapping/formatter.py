"""
Support for the 'format' key in the swagger spec as outlined in
https://github.com/swagger-api/swagger-spec/blob/master/versions/2.0.md#dataTypeFormat
"""
import dateutil

from bravado.mapping import schema


def register_format(format, to_wire, to_python, description=None):
    """
    Register a formatter for a given 'format'.

    :type format: string
    :param to_wire: single argument callable that converts a value to wire
        format
    :param to_python: single argument callable that converts a value to python
    :param description: useful description
    """
    _formatters[format] = (to_wire, to_python, description)


def to_wire(spec, value):
    """Converts a python primitive or object to a reasonable wire
    representation given the 'format' in the given spec.

    :param spec: spec for a primitive type as a dict
    :type value: int, long, float, boolean, string, unicode, etc
    :rtype: int, long, float, boolean, string, unicode, etc
    """
    if value is None or not schema.has_format(spec):
        return value

    to_wire, _, _ = _formatters[schema.get_format(spec)]
    return to_wire(value)


def to_python(spec, value):
    """Converts a value in wire format to its python representation given
    the 'format' in the given spec.

    :param spec: spec for a primitive type as a dict
    :type value: int, long, float, boolean, string, unicode, etc
    :rtype: int, long, float, boolean, string, object, etc
    """
    if value is None or not schema.has_format(spec):
        return value

    _, to_python, _ = _formatters[schema.get_format(spec)]
    return to_python(value)


# Default registered formats
_formatters = {
    'date': (
        lambda d: d.isoformat(),
        lambda d: dateutil.parser.parse(d).date(),
        'Converts string:date <=> python datetime.date'),
    'date-time': (
        lambda dt: dt.isoformat(),
        lambda dt: dateutil.parser.parse(dt),
        'Converts string:date-time <=> python datetime.datetime'),
    'int64': (
        lambda i: i if isinstance(i, long) else long(i),
        lambda i: i if isinstance(i, long) else long(i),
        'Converts integer:int64 <==> python long'),
    'int32': (
        lambda i: i if isinstance(i, int) else int(i),
        lambda i: i if isinstance(i, int) else int(i),
        'Converts integer:int32 <==> python int'),
    'float': (
        lambda f: f if isinstance(f, float) else float(f),
        lambda f: f if isinstance(f, float) else float(f),
        'Converts number:float <==> python float'),
    'double': (
        lambda d: d if isinstance(d, float) else float(d),
        lambda d: d if isinstance(d, float) else float(d),
        'Converts number:double <==> python float'),
    'byte': (
        lambda b: b if isinstance(b, str) else str(b),
        lambda b: b if isinstance(b, str) else str(b),
        'Converts string:byte <==> python str'),
}
