import urllib

import jsonschema

from bravado.exception import SwaggerError

# TODO: generalize for any Swagger Spec object, not just parameters

def validate_primitive(param, value):
    if value is None and param.has_default():
        value = param.default

    if param.required and value is None:
        raise SwaggerError('Parameter {0} cannot be null'.format(param.name))

    jsonschema.validate(value, param.jsonschema)

    # TODO: transform
    return value


def marshal_primitive(param, value, request):
    if param.location == 'path':
        token = u'{%s}' % param.name
        request['url'] = request['url'].replace(token, urllib.quote(unicode(value)))
    elif param.location == 'query':
        request['params'][param.name] = value
    elif param.location == 'header':
        request['headers'][param.name] = value
    elif param.location == 'formData':
        raise NotImplementedError('TODO')
    elif param.location == 'body':
        raise NotImplementedError('TODO')
    else:
        raise SwaggerError(
            "Don't know how to marshal_primitive with location {0}".
            format(param.location))


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


def marshal_array(param, value, request):
    if param.location == 'query':
        request['params'][param.name] = value
    elif param.location == 'header':
        request['headers'][param.name] = value
    elif param.location == 'formData':
        raise NotImplementedError('TODO')
    elif param.location == 'body':
        raise NotImplementedError('TODO')
