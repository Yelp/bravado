# -*- coding: utf-8 -*-
"""Code to check the validity of swagger types and conversion to python types
"""

import datetime

import dateutil.parser

from exception import SwaggerError

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


class SwaggerTypeCheck(object):
    """Initialization of the class checks for the validity
    of the value to the type.

    Raises TypeError/AssertionError if validation fails
    """

    def __init__(self, name, value, type_, models=None, allow_null=False):
        """Ctor to set params and then check the value

        :param name: name of the field, used for error logging
        :type name: str
        :param value: JSON value
        :type value: dict
        :param type_: type against which the value is to be validated
        :type type_: str or unicode
        :param models: namedtuple which maps complex type string to py type
        :type models: namedtuple
        :param allow_null: if True, ignores null values from type check
        :type allow_null: boolean
        """
        self.name = name
        self.value = value
        self._type = type_
        self.models = models
        self.allow_null = allow_null
        self._check_value_format()

    def _check_value_format(self):
        """Check the value as per the type of the value
        """
        if self._type == 'void':
            # Ignore any check if type is 'void'
            return
        elif self.allow_null and self.value is None:
            return
        elif is_primitive(self._type):
            self._check_primitive_type()
        elif is_array(self._type):
            self._check_array_type()
        else:
            # Ignore check if models tuple is not provided
            if self.models:
                self._check_complex_type()

    def _check_primitive_type(self):
        """Validate value is of primitive type
        Also converts swagger type to py type if needed e.g. datetime
        """
        ptype = get_primitive_mapping(self._type)
        if not isinstance(self.value, ptype):
            # convert string datetime to python datetime format
            if ptype == datetime.datetime:
                self.value = dateutil.parser.parse(self.value)
            elif ptype == datetime.date:
                self.value = dateutil.parser.parse(self.value).date()
            else:
                # For all the other cases, raise Type mismatch
                raise TypeError("%s's value: %s should be in types %r" % (
                    self.name, self.value, ptype))

    def _check_array_type(self):
        """Validate array type value is actually array type
        Also recursively converts value array to list of item array types
        """
        if self.value is None:
            raise TypeError("Array found as null")
        if self.value.__class__ is not list:
            raise TypeError("%r should be an array instead of %s" %
                            (self.value, self.value.__class__.__name__))
        array_item_type = get_array_item_type(self._type)
        self.value = [SwaggerTypeCheck(
            "%s's item" % self.name,
            item, array_item_type, self.models, self.allow_null).value
            for item in self.value]

    def _check_complex_type(self):
        """Checks all the fields in the complex type are of proper type
        All the required fields are present and no extra field is present
        """
        klass = self.models[self._type]
        if isinstance(self.value, klass):
            self.value = self.value._flat_dict()
        # The only valid type from this point on is JSON dict
        if not isinstance(self.value, dict):
            raise TypeError("Type for %s is expected to be object" %
                            self.value)
        required = list(klass._required) if klass._required else []
        for key in self.value.keys():
            if key in required:
                required.remove(key)
            if key not in klass._swagger_types.keys():
                # Ignore unrecognized keys
                continue
            self.value[key] = SwaggerTypeCheck(key,
                                               self.value[key],
                                               klass._swagger_types[key],
                                               self.models,
                                               self.allow_null).value
        if required:
            raise AssertionError("These required fields not present: %s" %
                                 required)
