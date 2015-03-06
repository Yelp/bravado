import logging
import jsonref

from exception import SwaggerError

log = logging.getLogger(__name__)


SWAGGER20_PRIMITIVES = (
    'integer',
    'number',
    'string',
    'boolean',
    'null'     # TODO: Do we need this?
)


def get_swagger_type(spec):
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


    :param spec: object spec in dict form
    :rtype: str
    """
    # TODO: If the type is not specified, isn't it assumed to be 'object'? Find
    #       docs where this is stated. #/definitions/{def_name}/ don't have
    #       a 'type' but it always seems to be assumed as 'object'
    # TODO: this is only used by the docstring stuff. consider moving to
    #       docstring.py
    obj_type = spec.get('type')
    obj_format = spec.get('format')
    ref = spec.get('$ref')
    if obj_format and obj_type:
        return "{0}:{1}".format(obj_type, obj_format)
    elif obj_type == 'array':
        return "{0}:{1}".format(obj_type, get_swagger_type(spec["items"]))
    elif ref:
        return ref
    elif obj_type:
        return obj_type
    else:
        raise SwaggerError("No proper type could be found from %s" % spec)


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
