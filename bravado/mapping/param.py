from functools import partial
import logging
import urllib
import simplejson as json

from bravado.mapping.exception import SwaggerMappingError
from bravado.mapping.http_client import APP_JSON
from bravado.mapping.marshal import marshal_schema_object
from bravado.mapping.unmarshal import unmarshal_schema_object
from bravado.mapping.validate import validate_schema_object

log = logging.getLogger(__name__)

# 'multi' left out intentionally - http client lib should handle it
COLLECTION_FORMATS = {
    'csv': ',',
    'ssv': ' ',
    'tsv': '\t',
    'pipes': '|'
}


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
    :raises: SwaggerMappingError when param location is not valid
    """
    location = param.location
    if location in ('path', 'query', 'header', 'formData'):
        return param.param_spec
    if location == 'body':
        return param.param_spec['schema']
    raise SwaggerMappingError(
        "Don't know how to handle location {0}".format(location))


def marshal_param(param, value, request):
    """
    Given an operation parameter and its value, marshal the value and place it
    in the proper request destination.

    Destination is one of:
        - path - can accept primitive and array of primitive types
        - query - can accept primitive and array of primitive types
        - header - can accept primitive and array of primitive types
        - body - can accept any type
        - formData - can accept primitive and array of primitive types

    :type param: :class:`bravado.mapping.param.Param`
    :param value: The value to assign to the parameter
    :type request: dict
    """
    spec = get_param_type_spec(param)
    location = param.location
    value = marshal_schema_object(param.swagger_spec, spec, value)
    validate_schema_object(spec, value)

    if spec['type'] == 'array' and location != 'body':
        value = apply_collection_format(spec, value)

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
            request.setdefault('data', {})[param.name] = value
    elif location == 'body':
        request['headers']['Content-Type'] = APP_JSON
        request['data'] = json.dumps(value)
    else:
        raise SwaggerMappingError(
            "Don't know how to marshal_param with location {0}".
            format(location))


def unmarshal_param(param, request):
    """Unmarshal the given parameter from the passed in request like object.

    :type param: :class:`bravado.mapping.param.Param`
    :type request: :class:`bravado.mapping.request.RequestLike`
    """
    param_spec = get_param_type_spec(param)
    location = param.location

    # TODO: handle collectionFormat
    #if spec['type'] == 'array' and location != 'body':
    #    value = apply_collection_format(spec, value)

    cast_param = partial(cast_request_param, param_spec['type'], param.name)

    if location == 'path':
        raw_value = cast_param(request.path.get(param.name, None))
    elif location == 'query':
        raw_value = cast_param(request.params.get(param.name, None))
    elif location == 'header':
        raw_value = cast_param(request.headers.get(param.name, None))
    elif location == 'formData':
        if param_spec['type'] == 'file':
            raw_value = request.params.get(param.name, None)
        else:
            raw_value = cast_param(request.params.get(param.name, None))
    elif location == 'body':
        # TODO: verify content-type header
        raw_value = request.json()
    else:
        raise SwaggerMappingError(
            "Don't know how to unmarshal_param with location {0}".
            format(location))

    validate_schema_object(param_spec, raw_value)
    value = unmarshal_schema_object(param.swagger_spec, param_spec, raw_value)
    return value


CAST_TYPE_TO_FUNC = {
    'integer': int,
    'float': float,
    'boolean': bool,
}


def cast_request_param(param_type, param_name, param_value):
    """Try to cast a request param (e.g. query arg, POST data) from a string to
    its specified type in the schema. This allows validating non-string params.

    :param param_type: name of the type to be casted to
    :type  param_type: string
    :param param_name: param name
    :type  param_name: string
    :param param_value: param value
    :type  param_value: string
    """
    if param_value is None:
        return None

    try:
        return CAST_TYPE_TO_FUNC.get(param_type, lambda x: x)(param_value)
    except ValueError:
        log.warn("Failed to cast %s value of %s to %s",
                 param_name, param_value, param_type)
        # Ignore type error, let jsonschema validation handle incorrect types
        return param_value


def add_file(param, value, request):
    """Add a parameter of type 'file' to the given request.

    :type param: :class;`bravado.mapping.param.Param`
    :param value: The raw content of the file to be uploaded
    :type request: dict
    """
    if request.get('files') is None:
        # support multiple files by default by setting to an empty array
        request['files'] = []

        # The http client should take care of setting the content-type header
        # to 'multipart/form-data'. Just verify that the swagger spec is
        # conformant
        expected_mime_type = 'multipart/form-data'

        # TODO: Remove after https://github.com/Yelp/swagger_spec_validator/issues/22 is implemented  # noqa
        if expected_mime_type not in param.op.consumes:
            raise SwaggerMappingError((
                "Mime-type '{0}' not found in list of supported mime-types for "
                "parameter '{1}' on operation '{2}': {3}").format(
                    expected_mime_type,
                    param.name,
                    param.op.operation_id,
                    param.op.consumes
                ))

    file_tuple = ('file', (param.name, value))
    request['files'].append(file_tuple)


def apply_collection_format(spec, value):
    """
    For an array, apply the collection format and return the result.

    :param spec: spec of the parameter with 'type': 'array'
    :param value: array value of the parmaeter
    :return: transformed value as a string
    """
    collection_format = spec.get('collectionFormat', 'csv')

    if collection_format == 'multi':
        # http client lib should handle this
        return value

    sep = COLLECTION_FORMATS[collection_format]
    return sep.join(str(element) for element in value)
