import jsonschema
from bravado import swagger_type

from bravado.exception import SwaggerError

# TODO: generalize for any Swagger Spec object, not just parameters
from bravado.mapping.model import is_model, MODEL_MARKER
from bravado.swagger_type import SWAGGER20_PRIMITIVES, is_list_like, \
    is_dict_like


def validate_primitive(param, value):
    if value is None and param.has_default():
        value = param.default

    if param.required and value is None:
        raise SwaggerError('Parameter {0} cannot be null'.format(param.name))

    jsonschema.validate(value, param.jsonschema)

    # TODO: transform
    return value


# def marshal_primitive(param, value, request):
#     if param.location == 'path':
#         token = u'{%s}' % param.name
#         request['url'] = request['url'].replace(token, urllib.quote(unicode(value)))
#     elif param.location == 'query':
#         request['params'][param.name] = value
#     elif param.location == 'header':
#         request['headers'][param.name] = value
#     elif param.location == 'formData':
#         raise NotImplementedError('TODO')
#     elif param.location == 'body':
#         raise NotImplementedError('TODO')
#     else:
#         raise SwaggerError(
#             "Don't know how to marshal_primitive with location {0}".
#             format(param.location))


def validate_array(param, value):
    if value is None and param.has_default():
        # Wrap if necessary - spec is weird about this
        if type(param.default) == list:
            value = param.default
        else:
            value = [param.default]

    if param.required and value is None:
        raise SwaggerError('Parameter {0} cannot be null'.format(param.name))

    jsonschema.validate(value, param.jsonschema)
    return value


# def marshal_array(param, value, request):
#     if param.location == 'query':
#         request['params'][param.name] = value
#     elif param.location == 'header':
#         request['headers'][param.name] = value
#     elif param.location == 'formData':
#         raise NotImplementedError('TODO')
#     elif param.location == 'body':
#         raise NotImplementedError('TODO')
#


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

    if obj_type in SWAGGER20_PRIMITIVES:
        return marshal_primitive(schema_object_spec, value)

    elif obj_type == 'array':
        return marshal_array(swagger_spec, schema_object_spec, value)

    elif is_model(schema_object_spec):
        # It is important that the 'model' check comes before 'object' check.
        # Model specs also have type 'object' but also have the additional
        # MODEL_MARKER key for identification.
        return marshal_model(swagger_spec, schema_object_spec, value)

    elif obj_type == 'object':
        return marshal_object(swagger_spec, schema_object_spec, value)

    else:
        raise SwaggerError('Unknown type {0} for value {1}'.format(
            obj_type, value))


def marshal_primitive(primitive_spec, value):
    if not type(value) in swagger_type.PY_PRIMITIVES:
        raise TypeError('Expected {0} type for {1}:{2}'.format(
            primitive_spec['type'], type(value), value))

    # TODO: validate
    # TODO: transform based on format
    return value


def marshal_array(swagger_spec, array_spec, value):
    if not is_list_like(value):
        raise TypeError('Expected list like type for {0}:{1}'.format(
            type(value), value))

    result = []
    for element in value:
        result.append(marshal_schema_object(swagger_spec, array_spec['items'], element))
    return result


def marshal_object(swagger_spec, object_spec, object_value):
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