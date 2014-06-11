#
# Copyright (c) Yelp, Inc.
#

"""Code for checking the validity of swagger types and conversion to python types
"""

from datetime import datetime
from swaggerpy.processors import SwaggerError

# Tuple is added to allow a response '4' which is of
# python type 'int' but swagger_type could be 'int64'
# so ('int', 'long') both are allowed for swagger 'int64'
PRIMITIVE_TYPE_MAPPING = {
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


PRIMITIVE_TYPE_TO_FORMAT = {
        u'integer': ['int32', 'int64'],
        u'number': ['float', 'double'],
        u'string': ['byte', 'date', 'date-time'],
        u'boolean': [],
        u'File': []
        }


CONTAINER_MAPPING = {
        u'array': list
        }


def primitive_formats():
    """returns Swagger primitive formats allowed after internal conversion.

       :returns: a list of typed formats eg. ['integer:int64', 'string:str']
       :rtype: list
    """
    return [_type + ":" + _format for _type in primitive_types()
                            for _format in PRIMITIVE_TYPE_TO_FORMAT[_type]]


def primitive_types():
    """returns all allowed Swagger primitive types

       :returns: a list of only types
       :rtype: list
    """
    return PRIMITIVE_TYPE_TO_FORMAT.keys()


def extract_format(_type_format):
    """returns the Format extracted from Type:Format
       Type:Format is the convention followed for type conversion to string

       :param _type_format: converted internal type format eg. "integer:int64"
       :type _type_format: str or unicode
       :returns: extracted format eg. "int64"
    """
    return _type_format.split(':')[1]


def get_primitive_mapping(_type):
    """returns Python type from swagger internal type string
       :param _type: swagger type, eg. integer, number:float
       :type _type: str or unicode
       :rtype: type eg. int, string
    """
    if _type in primitive_formats():
        _type = extract_format(_type)
    return PRIMITIVE_TYPE_MAPPING[_type]


def container_types():
    """returns all allowed container types in Swagger
       eg. "array"
       :rtype: list
    """
    return CONTAINER_MAPPING.keys()


def is_primitive(_type):
    """checks whether the swagger type is primitive
       :rtype: boolean
    """
    return _type in (primitive_types() + primitive_formats())


def is_array(_type):
    """checks whether the swagger type is array
       :rtype: boolean
    """
    return _type.startswith('array:')


def is_complex(_type):
    """checks whether the swagger type is neither primitive nor array
       :rtype: boolean
    """
    return not is_primitive(_type) and not is_array(_type)


def get_subtype_array(_type):
    """returns the Array Type extracted from Array:ArrayType
       Array:ArrayType is the convention followed for array type conversion to string

       :param _type: converted internal type format eg. "array:integer:int64"
       :type _type: str or unicode
       :returns: extracted array type eg. "integer:int64"
    """
    return _type[6:]


def swagger_to_py_type(_type):
    """returns the python type from swagger type

       :param _type: swagger internal type
       :type _type: str or unicode
       :rtype: Python type
    """
    if is_array(_type):
        return list
    elif is_complex(_type):
        return None  # ToDo: Complex Type class to be fetched
    elif is_primitive(_type):
        py_type = get_primitive_mapping(_type)
        # If Tuple, just pick the first type
        if isinstance(py_type, tuple):
            py_type = py_type[0]
        return py_type
    raise TypeError("%s type not yet supported." % _type)


def swagger_to_py_type_string(_type):
    """returns the string repr of Python type.
       Used during docstring display of a Model

       :param _type: swagger internal type
       :type _type: str or unicode
       :rtype: str or unicode
    """
    if is_array(_type):
        return "%s(%s)" % (CONTAINER_MAPPING['array'].__name__,
                           swagger_to_py_type_string(_type[6:]))
    elif is_complex(_type):
        return _type
    return swagger_to_py_type(_type).__name__


def get_swagger_type(_json):
    """Converts swagger type from json to swagger internal type
       i.e. array is converted to array:array_type
            format is converted to type:format

       :param _json: dict containing type and rest of the data
       :type _json: dict
       :rtype: str or unicode
    """
    _type = _json.get('type')
    _format = _json.get('format')
    _ref = _json.get('$ref')
    if _format and _type:
        return _type + ":" + _format
    elif _type == "array":
        return _type + ":" + get_swagger_type(_json["items"])
    elif _ref:
        return _ref
    elif _type:
        return _type
    else:
        raise SwaggerError("No proper type could be found from %s" % _json)


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
