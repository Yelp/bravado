# -*- coding: utf-8 -*-
"""Code to check the validity of swagger types and conversion to python types
"""

import datetime
import dateutil.parser
import logging
import jsonref

from exception import SwaggerError

log = logging.getLogger(__name__)

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
    'date': datetime.date,
    'date-time': datetime.datetime,
    'byte': bytes,
    'File': file
}

SWAGGER20_PRIMITIVES = (
    'integer',
    'number',
    'string',
    'boolean',
    'null'     # TODO: Do we need this?
)

PY_PRIMITIVES = (
    int,
    long,
    str,
    unicode,
    bool,
    float,
)


SWAGGER_PRIMITIVE_TYPE_TO_SWAGGER_FORMAT = {
    u'integer': ['int32', 'int64'],
    u'number': ['float', 'double'],
    u'string': ['byte', 'date', 'date-time'],
    u'boolean': [],
    u'File': []
}

# 1 array A JSON array.
# 2 boolean A JSON boolean.
# 3 integer A JSON number without a fraction or exponent part.
# 4 number Any JSON number. Number includes integer.
# 5 null The JSON null value.
# 6 object A JSON object.
# 7 string A JSON string.


CONTAINER_MAPPING = {
    u'array': list,
    u'object': dict,
}


CONTAINER_TYPES = CONTAINER_MAPPING.keys()

ARRAY = 'array'

COLON = ':'

DATETIME_TYPES = set([datetime.datetime, datetime.date])


def get_instance(py_type):
    """Factory method to get default constructor invoked for the type

    .. note::

        get_instance() is meant to be called to get an instance of
        primitive Python type. datetime() and date() are primitives in Swagger
        but not Python, so return None for these.

    Complex models are already set to None in swagger_to_py_type(), hence
    this should be called only for values from SWAGGER_TO_PY_TYPE_MAPPING
    """
    if py_type is None:
        return None
    # datetime and date are not Python primitive types, return None for them.
    if py_type in DATETIME_TYPES:
        return None
    return py_type()


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
    """Returns the Python type from the swagger internal type string

    :param type_: swagger type, eg. integer, number:float
    :type  type_: str or unicode
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


def is_file(type_):
    """checks whether the swagger type is file
    :rtype: boolean
    """
    return type_ == 'File'


def is_array(type_):
    """checks whether the swagger type is array
    :rtype: boolean
    """
    return type_.startswith(ARRAY + COLON)


def is_object(type_):
    """Checks whether the swagger type is object
    :rtype: boolean
    """
    return type_ == 'object'


def is_complex(type_):
    """checks whether the swagger type is neither primitive nor array
    :rtype: boolean
    """
    return (not is_primitive(type_) and not is_array(type_)) or is_object(type_)


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

    Example:

    .. code-block:: python

        {
            ...
            "type": "array",
            "items": {
                 "type": "integer",
                 "format": "int64"
                 }
            ...
        }

    Returns:

    .. code-block:: python

        "array:integer:int64"


    :param json_: dict containing type and rest of the data
    :type  json_: dict
    :rtype: str or unicode
    """
    # TODO: If the type is not specified, isn't it assumed to be 'object'? Find
    #       docs where this is stated. #/definitions/{def_name}/ don't have
    #       a 'type' but it always seems to be assumed as 'object'
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


def is_dict_like(spec):
    """Since we're using jsonref, identifying dicts while inspecting a swagger
    spec is no longer limited to the dict type. This takes into account
    jsonref's proxy objects that dereference to a dict.

    :param spec: swagger object specification in dict form
    :rtype: boolean
    """
    if type(spec) == dict:
        return True
    if type(spec) == jsonref.JsonRef and type(spec.__subject__) == dict:
        return True
    return False


def is_list_like(spec):
    """Since we're using jsonref, identifying arrays while inspecting a swagger
    spec is no longer limited to the list type. This takes into account
    jsonref's proxy objects that dereference to a list.

    :param spec: swagger object specification in dict form
    :rtype: boolean
    """
    if type(spec) == list:
        return True
    if type(spec) == jsonref.JsonRef and type(spec.__subject__) == list:
        return True
    return False
