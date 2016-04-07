# -*- coding: utf-8 -*-
import contextlib
from copy import copy
from functools import partial
import logging
import os
import urllib
import six.moves.urllib_parse as urlparse

from swaggerpy import swagger_type
from swaggerpy.compat import json
from swaggerpy.exception import SwaggerError
from swaggerpy.http_client import SynchronousHttpClient
from swaggerpy.processors import SwaggerProcessor

SWAGGER_VERSIONS = [u"1.2"]

log = logging.getLogger(__name__)


# TODO: replace with swagger_schema_validator
class ValidationProcessor(SwaggerProcessor):
    """A processor that validates the Swagger model.
    """

    def process_resource_listing(self, resources, context):
        required_fields = [u'apis', u'swaggerVersion']
        validate_required_fields(resources, required_fields, context)

        if not resources[u'swaggerVersion'] in SWAGGER_VERSIONS:
            raise SwaggerError(
                u"Unsupported Swagger version %s" %
                resources[u'swaggerVersion'], context)

    def process_resource_listing_api(self, resources, listing_api, context):
        # removing 'description' as it is recommended but not required
        validate_required_fields(listing_api, [u'path'], context)

        if not listing_api[u'path'].startswith(u"/"):
            raise SwaggerError(u"Path must start with /", context)

    def process_api_declaration(self, resources, resource, context):
        required_fields = [u'swaggerVersion', u'basePath', u'apis']
        validate_required_fields(resource, required_fields, context)

        if not resource[u'swaggerVersion'] in SWAGGER_VERSIONS:
            raise SwaggerError(
                u"Unsupported Swagger version %s" %
                resource[u'swaggerVersion'], context)
        # Check model name and id consistency
        if u'models' in resource:
            for (model_name, model) in resource[u'models'].items():
                if model.get('id') and model_name != model[u'id']:
                    raise SwaggerError(u"Model id doesn't match name", context)

    def process_resource_api(self, resources, resource, api, context):
        required_fields = [u'path', u'operations']
        validate_required_fields(api, required_fields, context)

    # 'type' is MUST for operation as '$ref' isnt possible
    def process_operation(self, resources, resource, api, operation, context,
                          model_ids):
        required_fields = [u'method', u'nickname', u'parameters', u'type']
        validate_required_fields(operation, required_fields, context)
        allowed_types = (swagger_type.primitive_types() +
                         model_ids.get('model_ids') + ['void'])
        validate_type_or_ref(operation, model_ids, allowed_types, [], context)
        validate_params_body_or_form(operation)

    def process_parameter(self, resources, resource, api, operation, parameter,
                          context, model_ids):
        # TODO: check `consumes` in schema has proper header as per paramType
        required_fields = [u'name', u'paramType', u'type']
        validate_required_fields(parameter, required_fields, context)
        allowed_types = (swagger_type.primitive_types() +
                         model_ids.get('model_ids'))
        validate_type_or_ref(parameter, model_ids, allowed_types, [], context)

    def process_response_message(self, resources, resource, api, operation,
                                 response_message, context, model_ids):
        required_fields = [u'code', u'message']
        validate_required_fields(response_message, required_fields, context)

    def process_model(self, resources, resource, model, context):
        required_fields = [u'id', u'properties']
        validate_required_fields(model, required_fields, context)
        # TODO: Check "required" if present should be a list
        # Move property field name into the object
        for (prop_name, prop) in model[u'properties'].items():
            prop[u'name'] = prop_name

    def process_property(self, resources, resource, model, prop,
                         context, model_ids):
        required_fields = []
        validate_required_fields(prop, required_fields, context)
        # explicit validate special case: type OR ref must exist
        allowed_types = swagger_type.primitive_types()
        allowed_refs = model_ids.get('model_ids')
        validate_type_or_ref(prop, model_ids, allowed_types,
                             allowed_refs, None)


def is_file_scheme_uri(url):
    return urlparse.urlparse(url).scheme == u'file'


class FileEventual(object):
    """Adaptor which supports the :class:`crochet.EventualResult`
    interface for retrieving api docs from a local file.
    """

    class FileResponse(object):

        def __init__(self, data):
            self.data = data

        def json(self):
            return self.data

    def __init__(self, path):
        self.path = path

    def get_path(self):
        if not self.path.endswith('.json'):
            return self.path + '.json'
        return self.path

    def wait(self, timeout=None):
        with contextlib.closing(urllib.urlopen(self.get_path())) as fp:
            return self.FileResponse(json.load(fp))

    def cancel(self):
        pass


def start_request(http_client, url, request_options):
    """Download and parse JSON from a URL.

    :param http_client: a :class:`swaggerpy.http_client.HttpClient`
    :param url: url for api docs
    :param request_options: additional fields to send with the request
    :return: an object with a :func`wait` method which returns the api docs
    """
    if is_file_scheme_uri(url):
        return FileEventual(url)

    request_params = dict(
        method='GET',
        url=url,
        **request_options)
    return http_client.start_request(request_params)


def load_resource_listing(
        url,
        http_client,
        base_url=None,
        request_options=None):
    """Load a complete swagger api spec and return all schemas compiled
    into a single dict.

    :param url: url to the swagger spec (file or http)
    :param http_client: a :class:`swaggerpy.http_client.HttpClient` for
        performing the requests to fetch api documents.
    :param base_url: optional url to use as the base url for api doc paths
    :param request_options: mapping of additional fields to specify in
        the http request to fetch resources.
    """
    request_options = request_options or {}
    timeout = request_options.get('timeout', 5)
    base_url = base_url or url
    processor = ValidationProcessor()

    def get_eventual_for_api(api):
        return start_request(
            http_client,
            urlparse.urljoin(base_url + '/', api['path'].strip('/')),
            request_options)

    def add_api_docs(resource_listing):
        # Start all async requests
        eventuals = map(get_eventual_for_api, resource_listing['apis'])
        for api, eventual in zip(resource_listing['apis'], eventuals):
            api['api_declaration'] = eventual.wait(timeout=timeout).json()

    resource_listing = start_request(
        http_client,
        url,
        request_options
    ).wait(timeout=timeout).json()

    processor.pre_apply(resource_listing)

    # TODO: is this url used ?
    resource_listing['url'] = url
    add_api_docs(resource_listing)
    processor.apply(resource_listing)
    return resource_listing


def validate_required_fields(json, required_fields, context):
    """Checks a JSON object for a set of required fields.

    If any required field is missing, a :class:`SwaggerError` is raised.

    :param json: JSON object to check.
    :param required_fields: List of required fields.
    :param context: Current context in the API.
    """
    missing_fields = set(required_fields) - set(json)

    if missing_fields:
        raise SwaggerError(
            u"Missing fields: %s" % u', '.join(missing_fields), context)


# TODO: Adding the file scheme here just adds complexity to start_request()
# Is there a better way to handle this?
def load_file(resource_listing_file, http_client=None):
    """Loads a resource listing file.

    :param http_client: HTTP client interface.
    :param resource_listing_file: File name for a resource listing.
    :return: Processed object model from
    :raise: IOError: On error reading api-docs.
    """
    file_path = os.path.abspath(resource_listing_file)
    url = urlparse.urljoin(u'file:', urllib.pathname2url(file_path))
    # When loading from files, everything is relative to the resource listing
    dir_path = os.path.dirname(file_path)
    base_url = urlparse.urljoin(u'file:', urllib.pathname2url(dir_path))
    return load_url(url, http_client=http_client, base_url=base_url)


def load_url(url, http_client=None, **kwargs):
    """Loads a resource listing.

    :param resource_listing_url: URL for a resource listing.
    :param http_client: HTTP client interface.
    :param base_url:    Optional URL to be the base URL for finding API
                        declarations. If not specified, 'basePath' from the
                        resource listing is used.
    :return: Processed object model from
    :raise: IOError, URLError: On error reading api-docs.
    """
    http_client = http_client or SynchronousHttpClient()
    return load_resource_listing(url, http_client, **kwargs)


class docstring_property(object):
    def __init__(self, func):
        self.func = func

    def __get__(self, _cls, _owner):
        return self.func()


def create_model_type(model):
    """Create a dynamic class from the model data defined in the swagger spec.

    The docstring for this class is dynamically generated because generating
    the docstring is relatively expensive, and would only be used in rare
    cases for interactive debugging in a REPL.

    :param model: Resource model :class:`dict` with keys `id` and `properties`
    :returns: dynamic type created with attributes, docstrings attached
    :rtype: type
    """
    props = model['properties']
    name = str(model['id'])

    methods = dict(
        __doc__=docstring_property(partial(create_model_docstring, props)),
        __eq__=lambda self, other: compare(self, other),
        __init__=lambda self, **kwargs: set_props(self, **kwargs),
        __repr__=lambda self: create_model_repr(self),
        __dir__=lambda self: props.keys(),
        _flat_dict=lambda self: create_flat_dict(self),
        _swagger_types=swagger_type.get_swagger_types(props),
        _required=model.get('required'),
    )
    return type(name, (object,), methods)


def set_props(model, **kwargs):
    """Constructor for the generated type - assigns given or default values

       :param model: generated model type reference
       :type model: type
       :param kwargs: attributes to override default values of constructor
       :type kwargs: dict
    """
    types = getattr(model, '_swagger_types')
    arg_keys = kwargs.keys()
    for property_name, property_swagger_type in types.iteritems():
        # Assign all property values specified in kwargs
        property_value = None
        if property_name in arg_keys:
            property_value = kwargs[property_name]
            arg_keys.remove(property_name)
        setattr(model, property_name, property_value)
    if arg_keys:
        raise AttributeError(" %s are not defined for %s." % (arg_keys, model))


def create_model_docstring(props):
    """Generates a docstring for the type from the props

       :param props: dict containing properties of the type
       :type props: dict
       :returns: Generated string

    Example: ::

        "Pet": {
            "id": "Pet",
            "properties": {
                "id": {
                    "type": "integer",
                    "format": "int64",
                    "description": "unique identifier for the pet",
                },
                "category": {
                    "$ref": "Category"
                },
                "name": {
                    "type": "string"
                },
                "status": {
                    "type": "string",
                    "description": "pet status in the store",
                }
            }
        }

    Result: ::

        Attributes:

            category (Category)
            status (str) : pet status in the store
            name (str)
            id (long) : unique identifier for the pet
    """
    types = swagger_type.get_swagger_types(props)
    docstring = "Attributes:\n\n\t"
    for prop in props.keys():
        py_type = swagger_type.swagger_to_py_type_string(types[prop])
        docstring += ("%s (%s) " % (prop, py_type))
        if props[prop].get('description'):
            docstring += ": " + props[prop]['description']
        docstring += '\n\t'
    return docstring


def compare(first, second):
    """Compares the two types for equivalence.

    If a type composes another model types, .__dict__ recurse on those
    and compares again on those dict values
    """
    if not hasattr(second, '__dict__'):
        return False

    # Ignore any '_raw' keys
    def norm_dict(d):
        return dict((k, d[k]) for k in d if k != '_raw')

    return norm_dict(first.__dict__) == norm_dict(second.__dict__)


def create_flat_dict(model):
    """Generates __dict__ of the model traversing recursively
    each of the list item of an array and calling it again.
    While __dict__ only converts it on one level.

       :param model: generated model type reference
       :type model: type
       :returns: flat dict repr of the model

    Example: ::

        Pet(id=3, name="Name", photoUrls=["7"], tags=[Tag(id=2, name='T')])

    converts to: ::

        {'id': 3,
         'name': 'Name',
         'photoUrls': ['7'],
         'tags': [{'id': 2,
                   'name': 'T'}
                 ]
         }
    """
    if not hasattr(model, '__dict__'):
        return model
    model_dict = copy(model.__dict__)
    for k, v in model.__dict__.iteritems():
        if isinstance(v, list):
            model_dict[k] = [create_flat_dict(x) for x in v if x is not None]
        elif v is None:
            # Remove None values from dict to avoid their type checking
            if model._required and k in model._required:
                raise AttributeError("Required field %s can not be None" % k)
            model_dict.pop(k)
        else:
            model_dict[k] = create_flat_dict(v)
    return model_dict


def create_model_repr(model):
    """Generates the repr string for the model

       :param model: generated model type reference
       :type model: type
       :returns: repr string for the model
    """
    string = ""
    separator = ""
    for prop in getattr(model, '_swagger_types').keys():
        string += ("%s%s=%r" % (separator, prop, getattr(model, prop)))
        separator = ", "
    return ("%s(%s)" % (model.__class__.__name__, string))


# TODO: should be part of swagger_schema_validator
def validate_params_body_or_form(json):
    """Validates that form request parameters are present or
    body request params but not both
    """
    has_body = any(param.get('paramType') == 'body'
                   for param in json['parameters'])
    has_form = any(param.get('paramType') == 'form'
                   for param in json['parameters'])
    if has_body and has_form:
        raise AttributeError("Both `form` and `body` param types present!")


# TODO: should be part of swagger_schema_validator
def validate_type_or_ref(json, model_ids, allowed_types,
                         allowed_refs, context):
    """Validates that either type OR ref is present in the json

       :param json: dict to check whether type or ref is present
       :param model_ids: list of allowed $ref ids (all models)
       :param allowed_types: list of all kind of types allowed
       :param allowed_refs: list of all kind of refs allowed
       :param context: only used for Request Operation and Paramter
    """
    if json.get(u'type') in swagger_type.CONTAINER_TYPES:
        validate_required_fields(json, [u'items'], context)
        # OVerride allowed_refs to add model_ids if empty
        allowed_refs = model_ids.get('model_ids')
        return validate_type_or_ref(json[u'items'], model_ids,
                                    allowed_types, allowed_refs, context)
    if json.get(u'type') not in allowed_types and \
       json.get(u'$ref') not in allowed_refs:
        # Show more detailed error with context, if present
        if context:
            raise SwaggerError("%s not in allowed types: %s" % (
                json.get(u'type'), allowed_types), context)
        else:
            raise TypeError("%s not in allowed types: %s" % (
                json.get(u'type') or
                json.get(u'$ref'), allowed_types + allowed_refs))
