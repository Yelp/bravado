"""
Delegate as much validation as possible out to jsonschema. This module serves
as the single point of entry for validations should we need to further
customize the behavior.
"""

import jsonschema

from bravado.mapping import schema


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
