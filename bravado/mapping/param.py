import urllib
import simplejson as json

from bravado import swagger_type
from bravado.exception import SwaggerError
from bravado.http_client import APP_JSON
from bravado.mapping.marshal import validate_primitive, marshal_primitive, \
    validate_array, marshal_array, marshal_schema_object
from bravado.mapping.schema import to_primitive_schema, to_array_schema
from bravado.swagger_type import SwaggerTypeCheck, SWAGGER20_PRIMITIVES, \
    is_dict_like, is_list_like
from bravado.mapping.model import is_model


# TODO: remove
def validate_and_add_params_to_request(spec, param_spec, value, request):
    """Validates if a required param_spec is given and wraps 'add_param_to_req'
    to populate a valid request.

    :type spec: :class:`bravado.mapping.spec.Spec`
    :param param_spec: parameter spec in json-like dict form
    :param value: value of the parameter passed into the operation invocation
    :param request: request object to be populated in dict form
    """
    # If param_spec not given in args, and not required, just ignore.
    if not param_spec.get('required') and value is None:
        return

    models = spec.definitions
    param_name = param_spec['name']
    location = param_spec['in']
    if location == 'body':
        type_ = swagger_type.get_swagger_type(param_spec['schema'])
    else:
        type_ = swagger_type.get_swagger_type(param_spec)

    if location == 'path':
        # Parameters in path need to be primitive/array types
        if swagger_type.is_complex(type_):
            raise TypeError(
                "Path parameter {0} with value {1} can only be primitive/list"
                .format(param_name, value))
    elif location == 'query':
        # Parameters in query need to be only primitive types
        if not swagger_type.is_primitive(type_) and not swagger_type.is_array(type_):
            raise TypeError(
                "Query parameter {0} with value {1} can only be primitive/list"
                .format(param_name, value))

    # TODO: this needs to move to add_param_to_req, and change logic
    # Allow lists for query params even if type is primitive
    #if isinstance(value, list) and location == 'query':
    #    type_ = swagger_type.ARRAY + swagger_type.COLON + type_

    # Check the parameter value against its type
    # And store the refined value back
    value = SwaggerTypeCheck(param_name, value, type_, models).value

    # If list in path, Turn list items into comma separated values
    if isinstance(value, list) and location == 'path':
        value = u",".join(str(x) for x in value)

    # Add the parameter value to the request object
    if value is not None:
        add_param_to_req(param_spec, value, request)
    else:
        if param_spec.get(u'required'):
            raise TypeError(u"Missing required parameter '%s'" % param_name)


# TODO: remove
def add_param_to_req(param_spec, value, request):
    """Populates request object with the request parameters

    :param param_spec: parameters spec in json-like dict form
    :param value: value for the param given in the API call
    :param request: request object to be populated
    :type request: dict
    """
    param_name = param_spec['name']
    location = param_spec['in']

    # TODO: remove copy/pasta
    if location == 'body':
        type_ = swagger_type.get_swagger_type(param_spec['schema'])
    else:
        type_ = swagger_type.get_swagger_type(param_spec)

    if location == u'path':
        request['url'] = request['url'].replace(
            u'{%s}' % param_name,
            urllib.quote(unicode(value)))
    elif location == u'query':
        request['params'][param_name] = value
    elif location == u'body':
        if not swagger_type.is_primitive(type_):
            # If not primitive, body has to be 'dict'
            # (or has already been converted to dict from model_dict)
            request['headers']['content-type'] = APP_JSON
            request['data'] = json.dumps(value)
        else:
            request['data'] = stringify_body(value)
    elif location == 'formData':
        handle_form_param(param_name, value, type_, request)
    elif location == 'header':
        request['headers'][param_name] = value
    else:
        raise AssertionError(u"Unsupported Parameter type: %s" % location)


def stringify_body(value):
    """Json dump the value to string if not already in string
    """
    if not value or isinstance(value, basestring):
        return value
    return json.dumps(value)


def handle_form_param(name, value, type_, request):
    if swagger_type.is_file(type_):
        if 'files' not in request:
            request['files'] = {}
        request['files'][name] = value
    elif swagger_type.is_primitive(type_):
        if 'data' not in request:
            request['data'] = {}
        request['data'][name] = value
    else:
        raise AssertionError(
            u"%s neither primitive nor File" % name)

# TODO: generalize for other Swagger object types
class Param(object):
    """Thin wrapper around a param_spec dict that provides convenience functions
    for commonly requested parameter information

    :type swagger_spec: :class:`Spec`
    :type param_spec: parameter specification in dict form
    """
    def __init__(self, swagger_spec, param_spec):
        self.swagger_spec = swagger_spec
        self.param_spec = param_spec

        # # generated on demand and cached by @property
        # self._jsonschema = None

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

    # @property
    # def jsonschema(self):
    #     """Returns the closest approximation of this parameter's swagger spec
    #     in valid jsonschema. Cached and used for validation.
    #
    #     :rtype: dict
    #     """
    #     # TODO: handle all possible types of 'location'
    #     if self._jsonschema is None:
    #         if self.swagger_type in SWAGGER20_PRIMITIVES:
    #             # integer, number, boolean, null, string
    #             self._jsonschema = to_primitive_schema(self.param_spec)
    #         elif self.swagger_type == 'array':
    #             self._jsonschema = to_array_schema(self.param_spec)
    #         else:
    #             # object, Model
    #             raise NotImplementedError('TODO')
    #     return self._jsonschema

    def has_default(self):
        return 'default' in self.param_spec

    @property
    def default(self):
        return self.param_spec['default']


def marshal_param(param, value, request):
    """
    Given an operation parameter and its value, marshal the value and place it
    in the proper request destination.

    Destination is one of:
        - path - can only accept primitive types
        - query - can accept primitive and array of primitive types
        - header - can accept primitive and array of primitive types
        - body - can accept any type
        - formdata - TODO

    :type param: :class:`Param`
    :param value: The value to assign to the parameter
    :type request: dict
    """
    location = param.location
    value = marshal_schema_object(param.swagger_spec, param.param_spec, value)

    if location == 'path':
        token = u'{%s}' % param.name
        request['url'] = request['url'].replace(token, urllib.quote(unicode(value)))
    elif location == 'query':
        request['params'][param.name] = value
    elif location == 'header':
        request['headers'][param.name] = value
    elif location == 'formData':
        raise NotImplementedError('TODO')
    elif location == 'body':
        # TODO: revisit
        request['data'] = json.dumps(value)
    else:
        raise SwaggerError(
            "Don't know how to marshal_param with location {0}".
            format(location))
