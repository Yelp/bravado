"""
Delegate as much validation as possible out to jsonschema. This module serves
as the single point of entry for validations should we need to further
customize the behavior.
"""
from bravado.mapping.exception import SwaggerMappingError
from bravado.mapping.schema import SWAGGER_PRIMITIVES

import jsonschema

from bravado.mapping import schema


def validate_schema_object(spec, value):
    obj_type = spec['type']

    if obj_type in SWAGGER_PRIMITIVES:
        validate_primitive(spec, value)

    elif obj_type == 'array':
        validate_array(spec, value)

    elif obj_type == 'object':
        validate_object(spec, value)

    # TODO: Support for 'file' type
    else:
        raise SwaggerMappingError('Unknown type {0} for value {1}'.format(
            obj_type, value))


def validate_primitive(spec, value):
    """
    :param spec: spec for a swagger primitive type in dict form
    :type value: int, string, float, long, etc
    """
    # Need to sanitize spec if it has the 'required' key.
    # jsonschema sees it as {'required' : ['propname1', 'propname2', ...]}
    # where as the Swagger spec uses it as {'required': True|False}.
    if schema.is_required(spec):
        spec = spec.copy()
        del spec['required']
    jsonschema.validate(value, spec)


def validate_array(spec, value):
    """
    :param spec: spec for an 'array' type in dict form
    :type value: list
    """
    jsonschema.validate(value, spec)


def validate_object(spec, value):
    """
    :param spec: spec for an 'object' type in dict form
    :type value: dict
    """
    jsonschema.validate(value, spec)
