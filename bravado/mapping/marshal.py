import urllib

import jsonschema

from bravado.mapping.schema import to_primitive_schema, to_array_schema
from bravado.swagger_type import SWAGGER20_PRIMITIVES
from bravado.exception import SwaggerError

# TODO: generalize for any Swagger Spec object, not just parameters
class Param(object):

    def __init__(self, swagger_object, param_spec):
        self.swagger_object = swagger_object
        self.param_spec = param_spec
        self._jsonschema = None  # use @property jsonschema

    @property
    def name(self):
        return self.param_spec['name']

    @property
    def location(self):
        # not using 'in' as the name since it is a keyword in python
        return self.param_spec['in']

    @property
    def description(self):
        return self.param_spec.get('description', None)

    @property
    def required(self):
        return self.param_spec.get('required', False)

    @property
    def swagger_type(self):
        """Return the swagger type

        :rtype: str
        """
        if self.location == 'body':
            return self.param_spec['schema']['type']
        return self.param_spec['type']

    @property
    def jsonschema(self):
        """Returns the closest approximation of this parameter's swagger spec
        in valid jsonschema.

        Caches so the jsonschema is only build one per parameter.

        :rtype: dict
        """
        # TODO: handle all possible types of 'location'
        if self._jsonschema is None:
            if self.swagger_type in SWAGGER20_PRIMITIVES:
                # integer, number, boolean, null, string
                self._jsonschema = to_primitive_schema(self.param_spec)
            elif self.swagger_type == 'array':
                self._jsonschema = to_array_schema(self.param_spec)
            else:
                # object, Model
                raise NotImplementedError('TODO')
        return self._jsonschema

    def has_default(self):
        return 'default' in self.param_spec

    @property
    def default(self):
        return self.param_spec['default']


def marshal_param(param, value, request):
    """
    Given data and a spec, converts it to wire format in the given request.

    :param data:
    :param spec:
    :param request:
    :return:
    """
    # path     => primitive
    # query    => primitite + array of primitives
    # header   => primitive + array of primitives
    # body     => primitive + array of (object or primitives) + object
    # formData =>
    location = param.location
    swagger_type = param.swagger_type

    if swagger_type in SWAGGER20_PRIMITIVES:
        value = validate_primitive(param, value)
        marshal_primitive(param, value, request)
    elif swagger_type == 'array' and location in ('query', 'header'):
        value = validate_array(param, value)
        marshal_array(param, value, request)
    else:
        raise NotImplementedError('TODO')


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
