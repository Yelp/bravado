import jsonschema

from bravado.exception import SwaggerError
from bravado.mapping import formatter, schema
from bravado.mapping.model import is_model, MODEL_MARKER
from bravado.mapping.schema import (
    is_dict_like,
    is_list_like,
    SWAGGER_PRIMITIVES
)


def unmarshal_schema_object(swagger_spec, schema_object_spec, value):
    """
    Unmarshal the value using the given schema object specification.

    Unmarshaling includes:
    - validate that the value conforms to the schema_object_spec
    - transform the value according to 'format' if available
    - return the value in a form suitable for use. e.g. conversion to a Model
      type.

    :type swagger_spec: :class:`bravado.mapping.spec.Spec`
    :type schema_object_spec: dict
    :type value: int, float, long, string, unicode, boolean, list, dict, etc
    :return: unmarshaled value
    :rtype: int, float, long, string, unicode, boolean, list, dict, object (in
        the case of a 'format' conversion', or Model type
    """
    obj_type = schema_object_spec['type']

    if obj_type in SWAGGER_PRIMITIVES:
        return unmarshal_primitive(schema_object_spec, value)

    elif obj_type == 'array':
        return unmarshal_array(swagger_spec, schema_object_spec, value)

    elif is_model(schema_object_spec):
        # It is important that the 'model' check comes before 'object' check.
        # Model specs also have type 'object' but also have the additional
        # MODEL_MARKER key for identification.
        return unmarshal_model(swagger_spec, schema_object_spec, value)

    elif obj_type == 'object':
        return unmarshal_object(swagger_spec, schema_object_spec, value)

    else:
        raise SwaggerError(
            "Don't know how to unmarshal value {0} with a value of {1}"
            .format(value, obj_type))


def unmarshal_primitive(spec, value):
    """Unmarshal a jsonschema primitive type into a python primitive.

    :type spec: dict or jsonref.JsonRef
    :type value: int, long, float, boolean, string, unicode, etc
    :rtype: int, long, float, boolean, string, unicode, or an object
        based on 'format'
    :raises: TypeError
    """
    if value is None and schema.is_required(spec):
        # TODO: Error message needs more context. Consider adding a stack like
        #       `context` object to each `unmarshal_*` method that acts like
        #       breadcrumbs.
        raise TypeError('Spec {0} says this is a required value'.format(spec))

    value = formatter.to_python(spec, value)
    jsonschema.validate(value, spec)
    return value


def unmarshal_array(swagger_spec, array_spec, array_value):
    """Unmarshal a jsonschema type of 'array' into a python list.

    :type swagger_spec: :class:`bravado.mapping.spec.Spec`
    :type array_spec: dict or jsonref.JsonRef
    :type array_value: list
    :rtype: list
    :raises: TypeError
    """
    if not is_list_like(array_value):
        raise TypeError('Expected list like type for {0}:{1}'.format(
            type(array_value), array_value))

    # TODO: could also do this in-place instead of allocating a new array. Think
    #       about implications of this some more...
    result = []
    for element in array_value:
        result.append(unmarshal_schema_object(
            swagger_spec, array_spec['items'], element))
    return result


def unmarshal_object(swagger_spec, object_spec, object_value):
    """Unmarshal a jsonschema type of 'object' into a python dict.

    :type swagger_spec: :class:`bravado.mapping.spec.Spec`
    :type object_spec: dict or jsonref.JsonRef
    :type object_value: dict
    :rtype: dict
    :raises: TypeError
    """
    if not is_dict_like(object_value):
        raise TypeError('Expected dict like type for {0}:{1}'.format(
            type(object_value), object_value))

    # TODO: could also do this in-place instead of allocating a new dict. Think
    #       about implications of this some more...
    result = {}
    props_spec = object_spec['properties']
    for prop_name, prop_spec in props_spec.iteritems():
        result[prop_name] = unmarshal_schema_object(
            swagger_spec, prop_spec, object_value.get(prop_name))
    return result


def unmarshal_model(swagger_spec, model_spec, model_value):
    """Unmarshal a dict into a Model instance.

    :type swagger_spec: :class:`bravado.mapping.spec.Spec`
    :type model_spec: dict or jsonref.JsonRef
    :type model_value: dict
    :rtype: Model instance
    :raises: TypeError
    """
    model_name = model_spec[MODEL_MARKER]
    model_type = swagger_spec.definitions.get(model_name, None)

    if model_type is None:
        raise TypeError(
            'Unknown model {0} when trying to unmarshal {1}'
            .format(model_name, model_value))

    if not is_dict_like(model_value):
        raise TypeError(
            "Expected type to be dict for value {0} to unmarshal to a {1}."
            "Was {1} instead."
            .format(model_value, model_type, type(model_value)))

    model_params = {}
    props_spec = model_spec['properties']
    for prop_name, prop_spec in props_spec.iteritems():
        model_params[prop_name] = unmarshal_schema_object(
            swagger_spec, prop_spec, model_value.get(prop_name, None))
    model_instance = model_type(**model_params)
    return model_instance
