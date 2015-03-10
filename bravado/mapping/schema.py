import jsonref


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
