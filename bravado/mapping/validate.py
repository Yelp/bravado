"""
Delegate as much validation as possible out to jsonschema. This module serves
as the single point of entry for validations should we need to further
customize the behavior.
"""
from bravado.mapping.exception import SwaggerMappingError
from bravado.mapping.schema import SWAGGER_PRIMITIVES
from bravado.mapping.swagger20_validator import Swagger20Validator


def validate_schema_object(spec, value):
    obj_type = spec['type']

    if obj_type in SWAGGER_PRIMITIVES:
        validate_primitive(spec, value)

    elif obj_type == 'array':
        validate_array(spec, value)

    elif obj_type == 'object':
        validate_object(spec, value)

    elif obj_type == 'file':
        pass

    else:
        raise SwaggerMappingError('Unknown type {0} for value {1}'.format(
            obj_type, value))


def validate_primitive(spec, value):
    """
    :param spec: spec for a swagger primitive type in dict form
    :type value: int, string, float, long, etc
    """
    Swagger20Validator(spec).validate(value)


def validate_array(spec, value):
    """
    :param spec: spec for an 'array' type in dict form
    :type value: list
    """
    Swagger20Validator(spec).validate(value)


def validate_object(spec, value):
    """
    :param spec: spec for an 'object' type in dict form
    :type value: dict
    """
    Swagger20Validator(spec).validate(value)
