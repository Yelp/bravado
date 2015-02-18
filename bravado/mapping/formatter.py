import datetime

from bravado.mapping import schema


def register_format(format, to_wire, from_wire, description=None):
    """
    Register a formatter for a given 'format'.

    :type format: string
    :param to_wire: single argument callable that encodes a value to wire format
    :param from_wire: single argument callable that decodes a value from wire
        format
    :param description: useful description
    """
    _formatters['format'] = (to_wire, from_wire, description)


def to_wire(spec, value):
    """Formats a value if its spec has a 'format' specifier.

    :param spec: spec for a primitive type as a dict
    :type value: int, long, float, boolean, string, unicode, etc
    :return: value (default may be provided in the spec)
    :raises: SwaggerError in validation failure
    """
    if not schema.has_format(spec):
        return value
    to_wire, _, _ = _formatters[schema.get_format(spec)]
    return to_wire(value)


def from_wire(spec, value):
    """Unformats a value if its spec has a 'format' specifier.

    :param spec: spec for a primitive type as a dict
    :type value: int, long, float, boolean, string, unicode, etc
    :return: value (default may be provided in the spec)
    :raises: SwaggerError in validation failure
    """
    if not schema.has_format(spec):
        return value
    _, from_wire, _ = _formatters[schema.get_format(spec)]
    return from_wire(value)


def date_to_wire(value):
    # TODO: None handling
    if type(value) == datetime.date:
        # TODO: Fix me - this is obviously not correct
        return str(value)


def date_from_wire(value):
    # TODO: None handling
    # TODO: Fix me - this is obviously not correct
    value = datetime.date(value)
    return value

# TODO: add other 'format' types
# TODO: revisit int64 formatters
_formatters = {
    'date': (date_to_wire, date_from_wire, 'Converts a date to/from a string'),
    'int64': (lambda i: long(i), lambda i: long(i),
              'Converts an integer to/from int64')
}
