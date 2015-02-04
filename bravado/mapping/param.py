import urllib
import simplejson as json


from bravado import swagger_type
from bravado.http_client import APP_JSON
from bravado.swagger_type import SwaggerTypeCheck


# TODO: Needs to be thought through some more instead of just carrying over
#       the impl from 1.2

def validate_and_add_params_to_request(spec, param_dict, value, request):
    """Validates if a required param_dict is given and wraps 'add_param_to_req'
    to populate a valid request.

    :type spec: :class:`bravado.mapping.spec.Spec`
    :param param_dict: parameter spec in json-like dict form
    :param value: value of the parameter passed into the operation invocation
    :param request: request object to be populated in dict form
    """
    # If param_dict not given in args, and not required, just ignore.
    if not param_dict.get('required') and value is None:
        return

    models = spec.definitions
    param_name = param_dict['name']
    type_ = swagger_type.get_swagger_type(param_dict)
    location = param_dict['in']

    if location == 'path':
        # Parameters in path need to be primitive/array types
        if swagger_type.is_complex(type_):
            raise TypeError(
                "Path parameter {0} with value {1} can only be primitive/list"
                .format(param_name, value))
    elif location == 'query':
        # Parameters in query need to be only primitive types
        if not swagger_type.is_primitive(type_):
            raise TypeError(
                "Query parameter {0} with value {1) can only be primitive"
                .format(param_name, value))

    # TODO: this needs to move to add_param_to_req, and change logic
    # Allow lists for query params even if type is primitive
    if isinstance(value, list) and location == 'query':
        type_ = swagger_type.ARRAY + swagger_type.COLON + type_

    # Check the parameter value against its type
    # And store the refined value back
    value = SwaggerTypeCheck(param_name, value, type_, models).value

    # If list in path, Turn list items into comma separated values
    if isinstance(value, list) and location == 'path':
        value = u",".join(str(x) for x in value)

    # Add the parameter value to the request object
    if value is not None:
        add_param_to_req(param_dict, value, request)
    else:
        if param_dict.get(u'required'):
            raise TypeError(u"Missing required parameter '%s'" % param_name)


def add_param_to_req(param_dict, value, request):
    """Populates request object with the request parameters

    :param param_dict: parameters spec in json-like dict form
    :param value: value for the param given in the API call
    :param request: request object to be populated
    :type request: dict
    """
    param_name = param_dict['name']
    type_ = swagger_type.get_swagger_type(param_dict)
    location = param_dict['in']

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
