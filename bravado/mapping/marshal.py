import jsonschema

from bravado.mapping.exception import SwaggerError
from bravado.mapping import schema
from bravado.mapping import formatter
from bravado.mapping.model import is_model, MODEL_MARKER
from bravado.mapping.schema import (
    is_dict_like,
    is_list_like,
    SWAGGER_PRIMITIVES
)


def marshal_schema_object(swagger_spec, schema_object_spec, value):
    """
    Marshal the value using the given schema object specification.

    Marshaling includes:
    - validate that the value conforms to the schema_object_spec
    - transform the value according to 'format' if available
    - return the value in a form suitable for 'on-the-wire' transmission

    :type swagger_spec: :class:`bravado.mapping.spec.Spec`
    :type schema_object_spec: dict
    :type value: int, long, string, unicode, boolean, list, dict, Model type
    :return: marshaled value
    :rtype: int, long, string, unicode, boolean, list, dict
    """
    obj_type = schema_object_spec['type']

    if obj_type in SWAGGER_PRIMITIVES:
        return marshal_primitive(schema_object_spec, value)

    if obj_type == 'array':
        return marshal_array(swagger_spec, schema_object_spec, value)

    if is_model(schema_object_spec):
        # It is important that the 'model' check comes before 'object' check.
        # Model specs also have type 'object' but also have the additional
        # MODEL_MARKER key for identification.
        return marshal_model(swagger_spec, schema_object_spec, value)

    if obj_type == 'object':
        return marshal_object(swagger_spec, schema_object_spec, value)

    # TODO: Support for 'file' type
    raise SwaggerError('Unknown type {0} for value {1}'.format(obj_type, value))


def marshal_primitive(spec, value):
    """Marshal a jsonschema primitive type into a python primitive.

    :type spec: dict or jsonref.JsonRef
    :type value: int, long, float, boolean, string, unicode, or an object
        based on 'format'
    :rtype: int, long, float, boolean, string, unicode, etc
    :raises: TypeError
    """
    default_used = False

    if value is None and schema.has_default(spec):
        default_used = True
        value = schema.get_default(spec)

    if value is None and schema.is_required(spec):
        raise TypeError('Spec {0} is a required value'.format(spec))

    if not default_used:
        value = formatter.to_wire(spec, value)

        # Need to sanitize spec if it has the 'required' key.
        # jsonschema sees it as {'required' : ['propname1', 'propname2', ...]}
        # where as a param_spec uses it as {'required': True|False}.
        if schema.is_required(spec):
            sanitized_spec = spec.copy()
            del sanitized_spec['required']
            jsonschema.validate(value, sanitized_spec)
        else:
            jsonschema.validate(value, spec)

    return value


def marshal_array(swagger_spec, array_spec, array_value):
    """Marshal a jsonschema type of 'array' into a json-like list.

    :type swagger_spec: :class:`bravado.mapping.spec.Spec`
    :type array_spec: dict or jsonref.JsonRef
    :type array_value: list
    :rtype: list
    :raises: TypeError
    """
    if not is_list_like(array_value):
        raise TypeError('Expected list like type for {0}:{1}'.format(
            type(array_value), array_value))

    result = []
    for element in array_value:
        result.append(marshal_schema_object(
            swagger_spec, array_spec['items'], element))
    return result


def marshal_object(swagger_spec, object_spec, object_value):
    """Marshal a jsonschema type of 'object' into a json-like dict.

    :type swagger_spec: :class:`bravado.mapping.spec.Spec`
    :type object_spec: dict or jsonref.JsonRef
    :type object_value: dict
    :rtype: dict
    :raises: TypeError
    """
    if not is_dict_like(object_value):
        raise TypeError('Expected dict like type for {0}:{1}'.format(
            type(object_value), object_value))

    result = {}
    props_spec = object_spec['properties']
    for prop_name, prop_spec in props_spec.iteritems():
        result[prop_name] = marshal_schema_object(
            swagger_spec, prop_spec, object_value.get(prop_name))
    return result


def marshal_model(swagger_spec, model_spec, model_value):
    """Marshal a Model instance into a json-like dict.

    :type swagger_spec: :class:`bravado.mapping.spec.Spec`
    :type model_spec: dict or jsonref.JsonRef
    :type model_value: Model instance
    :rtype: dict
    :raises: TypeError
    """
    model_name = model_spec[MODEL_MARKER]
    model_type = swagger_spec.definitions.get(model_name, None)

    if model_type is None:
        raise TypeError('Unknown model {0}'.format(model_name))

    if type(model_value) != model_type:
        raise TypeError('Expected model of type {0} for {1}:{2}'.format(
            model_name, type(model_value), model_value))

    result = {}
    props_spec = model_spec['properties']
    for prop_name, prop_spec in props_spec.iteritems():
        result[prop_name] = marshal_schema_object(
            swagger_spec, prop_spec, getattr(model_value, prop_name))
    return result
