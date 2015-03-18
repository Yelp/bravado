import jsonref

from bravado.mapping.exception import SwaggerMappingError

# 'object' and 'array' are omitted since this should really be read as
# "Swagger types that map to python primitives"
SWAGGER_PRIMITIVES = (
    'integer',
    'number',
    'string',
    'boolean',
    'null',
)


def has_default(schema_object_spec):
    return 'default' in schema_object_spec


def get_default(schema_object_spec):
    return schema_object_spec.get('default', None)


def is_required(schema_object_spec):
    return 'required' in schema_object_spec


def has_format(schema_object_spec):
    return 'format' in schema_object_spec


def get_format(schema_object_spec):
    return schema_object_spec.get('format', None)


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


def get_spec_for_prop(object_spec, object_value, prop_name):
    """Given a jsonschema object spec and value, retrieve the spec for the
     given property taking 'additionalProperties' into consideration.

    :param object_spec: spec for a jsonschema 'object' in dict form
    :param object_value: jsonschema object containing the given property
    :param prop_name: name of the property to retrieve the spec for
    :return: spec for the given property or None if no spec found
    :rtype: dict
    """
    spec = object_spec.get('properties', {}).get(prop_name)
    if spec is not None:
        return spec

    additional_props = object_spec.get('additionalProperties', True)

    if isinstance(additional_props, bool):
        # no spec for additional properties to conform to - this is basically
        # a way to send pretty much anything across the wire as is.
        return None

    if is_dict_like(additional_props):
        # spec that all additional props MUST conform to
        return additional_props

    raise SwaggerMappingError(
        "Don't know what to do with `additionalProperties` in spec {0}"
        "when inspecting value {1}".format(object_spec, object_value))
