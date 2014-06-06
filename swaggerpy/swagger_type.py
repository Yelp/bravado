from datetime import datetime

NoneType = None.__class__

PRIMITIVE_TYPE_MAPPING = {
            'int32': int,
            'int64': (long, int),
            'float': float,
            'double': float,
            'string': (str, unicode),
            'boolean': bool,
            'date': datetime,
            'date-time': datetime,
            'array': list,
            'byte': bytes,
            'void': NoneType,
            None: NoneType
            }


def is_primitive(_type):
    return _type in PRIMITIVE_TYPE_MAPPING.keys()


#array:XYZ and all $ref are complex types
def is_complex(_type):
    return not is_primitive(_type)


def is_array(_type):
    return _type.startswith('array:')


def get_subtype_array(_type):
    #strip 'array:'
    return _type[6:]


def swagger_to_py_type(_type):
    if is_array(_type):
        return "list(%s)" % swagger_to_py_type(_type[6:])
    if is_complex(_type):
        return _type
    py_type = PRIMITIVE_TYPE_MAPPING[_type]
    #If Tuple, just pick the first type
    if isinstance(py_type, tuple):
        py_type = py_type[0]
    return py_type.__name__


def get_subtype(_json):
    subtype = _json.get('items')
    return (subtype.get('$ref') or subtype.get('format') or subtype.get('type'))


def add_subtype_for_array(_type, _json):
    if _type == "array":
        return "array:" + get_subtype(_json)
    return _type


def get_swagger_types(props):
    swagger_types = {}
    for prop in props.keys():
        _type = props[prop].get('type')
        _format = props[prop].get('format')
        _ref = props[prop].get('$ref')
        if _format:
            swagger_types[prop] = _format
        elif _type == "array":
            swagger_types[prop] = add_subtype_for_array(_type, props[prop])
        elif _ref:
            swagger_types[prop] = _ref
        elif _type:
            swagger_types[prop] = _type
    return swagger_types
