import urllib
from bravado.mapping import schema
import simplejson as json

from bravado.mapping.exception import SwaggerMappingError
from bravado.http_client import APP_JSON
from bravado.mapping.marshal import marshal_schema_object


def stringify_body(value):
    """Json dump the value to string if not already in string
    """
    if not value or isinstance(value, basestring):
        return value
    return json.dumps(value)


class Param(object):
    """Thin wrapper around a param_spec dict that provides convenience functions
    for commonly requested parameter information.
    """
    def __init__(self, swagger_spec, op, param_spec):
        """
        :type swagger_spec: :class:`bravado.mapping.spec.Spec`
        :type op: :class:`bravado.mapping.operation.Operation`
        :type param_spec: parameter specification in dict form
        """
        self.op = op
        self.swagger_spec = swagger_spec
        self.param_spec = param_spec

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

    def has_default(self):
        return 'default' in self.param_spec

    @property
    def default(self):
        return self.param_spec['default']


def get_param_type_spec(param):
    """
    The spec for the parameter 'type' is not always in the same place for a
    parameter. The notable exception is when the location is 'body' and the
    schema for the type is in param_spec['schema']

    :rtype: dict
    :return: the param spec that contains 'type'
    """
    location = param.location
    if location in ('path', 'query', 'header', 'formData'):
        return param.param_spec
    if location == 'body':
        return param.param_spec['schema']
    raise Exception("Don't know how to handle location {0}".format(location))


def marshal_param(param, value, request):
    """
    Given an operation parameter and its value, marshal the value and place it
    in the proper request destination.

    Destination is one of:
        - path - can only accept primitive types
        - query - can accept primitive and array of primitive types
        - header - can accept primitive and array of primitive types
        - body - can accept any type
        - formData - can only accept primitive types

    :type param: :class:`Param`
    :param value: The value to assign to the parameter
    :type request: dict
    """
    spec = get_param_type_spec(param)
    location = param.location
    value = marshal_schema_object(param.swagger_spec, spec, value)

    if location == 'path':
        token = u'{%s}' % param.name
        request['url'] = \
            request['url'].replace(token, urllib.quote(unicode(value)))
    elif location == 'query':
        request['params'][param.name] = value
    elif location == 'header':
        request['headers'][param.name] = value
    elif location == 'formData':
        if spec['type'] == 'file':
            add_file(param, value, request)
        else:
            add_formdata(param, value, request)
    elif location == 'body':
        request['headers']['Content-Type'] = APP_JSON
        request['data'] = json.dumps(value)
    else:
        raise SwaggerMappingError(
            "Don't know how to marshal_param with location {0}".
            format(location))


def add_file(param, value, request):
    """Add a parameter of type 'file' to the given request.

    :type param: :class;`bravado.mapping.param.Param`
    :param value: The raw content of the file to be uploaded
    :type request: dict
    """
    if request.get('file') is None:
        # support multiple files by default by setting to an empty array
        request['file'] = []

        # The http client should take care of setting the content-type header
        # to 'multipart/form-data'. Just verify that the swagger spec is
        # conformant
        expected_mime_type = 'multipart/form-data'
        if expected_mime_type not in param.op.consumes:
            raise SwaggerMappingError((
                "Mime-type '{0}' not found in list of supported mime-types for "
                "parameter '{1}' on operation '{2}': {3}").format(
                    expected_mime_type,
                    param.name,
                    param.op.operation_id,
                    param.op.consumes
                ))

    file_tuple = ('files', (param.name, value))
    request['file'].append(file_tuple)


def add_formdata(param, value, request):
    # form parameter
    if request.get('data') is None:
        request['data'] = {}
    request['data'][param.name] = value
