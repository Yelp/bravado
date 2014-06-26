#
# Copyright (c) Yelp, Inc.
#

"""Code to check the validity of swagger types and conversion to python types
"""

from datetime import datetime

from swaggerpy.processors import SwaggerError

# Tuple is added to allow a response '4' which is of
# python type 'int' but swagger_type could be 'int64'
# so ('int', 'long') both are allowed for swagger 'int64'
SWAGGER_TO_PY_TYPE_MAPPING = {
    'int32': int,
    'int64': (long, int),
    'integer': (long, int),
    'float': float,
    'double': float,
    'number': float,
    'string': (str, unicode),
    'boolean': bool,
    'date': datetime,
    'date-time': datetime,
    'byte': bytes,
    'File': bytes
}


SWAGGER_PRIMITIVE_TYPE_TO_SWAGGER_FORMAT = {
    u'integer': ['int32', 'int64'],
    u'number': ['float', 'double'],
    u'string': ['byte', 'date', 'date-time'],
    u'boolean': [],
    u'File': []
}


CONTAINER_MAPPING = {
    u'array': list
}


CONTAINER_TYPES = CONTAINER_MAPPING.keys()

ARRAY = 'array'

COLON = ':'


def primitive_formats():
    """returns Swagger primitive formats allowed after internal conversion.

    :returns: a list of typed formats eg. ['integer:int64', 'string:str']
    :rtype: list
    """
    return [type_ + COLON + format_ for type_ in primitive_types()
            for format_ in SWAGGER_PRIMITIVE_TYPE_TO_SWAGGER_FORMAT[type_]]


def primitive_types():
    """returns all allowed Swagger primitive types

    :returns: a list of only types
    :rtype: list
    """
    return SWAGGER_PRIMITIVE_TYPE_TO_SWAGGER_FORMAT.keys()


def extract_format(_type_format):
    """returns the Format extracted from Type:Format
    Type:Format is the convention followed for type conversion to string

    :param _type_format: converted internal type format eg. "integer:int64"
    :type _type_format: str or unicode
    :returns: extracted format eg. "int64"
    """
    return _type_format.split(COLON)[1]


def get_primitive_mapping(type_):
    """returns Python type from swagger internal type string
    :param type_: swagger type, eg. integer, number:float
    :type type_: str or unicode
    :rtype: type eg. int, string
    """
    if type_ in primitive_formats():
        type_ = extract_format(type_)
    return SWAGGER_TO_PY_TYPE_MAPPING[type_]


def is_primitive(type_):
    """checks whether the swagger type is primitive
    :rtype: boolean
    """
    return type_ in (primitive_types() + primitive_formats())


def is_array(type_):
    """checks whether the swagger type is array
    :rtype: boolean
    """
    return type_.startswith(ARRAY + COLON)


def is_complex(type_):
    """checks whether the swagger type is neither primitive nor array
    :rtype: boolean
    """
    return not is_primitive(type_) and not is_array(type_)


def get_array_item_type(type_):
    """returns the Array Type extracted from 'Array:ArrayType'
    'Array:ArrayType' is the convention followed for
    converting swagger array type into a string

    :param type_: converted internal type format eg. "array:integer:int64"
    :type type_: str or unicode
    :returns: extracted array type eg. "integer:int64"
    """
    return type_[(len(ARRAY) + 1):]


def swagger_to_py_type(type_):
    """returns the python type from swagger type

    :param type_: swagger internal type
    :type type_: str or unicode
    :rtype: Python type
    """
    if is_array(type_):
        return list
    elif is_complex(type_):
        return None  # ToDo: Complex Type class to be fetched
    elif is_primitive(type_):
        py_type = get_primitive_mapping(type_)
        # If Tuple, just pick the first type
        if isinstance(py_type, tuple):
            py_type = py_type[0]
        return py_type
    raise TypeError("%s type not yet supported." % type_)


def swagger_to_py_type_string(type_):
    """returns the string repr of Python type.
    Used during docstring display of a Model

    :param type_: swagger internal type
    :type type_: str or unicode
    :rtype: str or unicode
    """
    if is_array(type_):
        return "%s(%s)" % (CONTAINER_MAPPING[ARRAY].__name__,
                           swagger_to_py_type_string(
                               get_array_item_type(type_)))
    elif is_complex(type_):
        return type_
    return swagger_to_py_type(type_).__name__


def get_swagger_type(json_):
    """Converts swagger type from json to swagger internal type
    i.e. array is converted to array:array_type
         format is converted to type:format

    :param json_: dict containing type and rest of the data
    :type json_: dict
    :rtype: str or unicode

    Example:
    ...
    "type": "array",
    "items": {
         "type": "integer",
         "format": "int64"
         }
    ...
    Returns: "array:integer:int64"
    """
    type_ = json_.get('type')
    format_ = json_.get('format')
    ref = json_.get('$ref')
    if format_ and type_:
        return type_ + COLON + format_
    elif type_ == 'array':
        return type_ + COLON + get_swagger_type(json_["items"])
    elif ref:
        return ref
    elif type_:
        return type_
    else:
        raise SwaggerError("No proper type could be found from %s" % json_)


def get_swagger_types(props):
    """Converts dict of swagger types to dict of swagger internal types

    :param props: dict of json properties
    :type props: dict
    :rtype: dict
    """
    swagger_types = {}
    for prop in props.keys():
        swagger_types[prop] = get_swagger_type(props[prop])
    return swagger_types
