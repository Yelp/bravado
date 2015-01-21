# -*- coding: utf-8 -*-
from copy import copy
from functools import partial
import logging
import os
import urllib
import urlparse

from swaggerpy import swagger_type
from swaggerpy.compat import json
from swaggerpy.http_client import SynchronousHttpClient
from swaggerpy.processors import SwaggerProcessor, SwaggerError

SWAGGER_VERSIONS = [u"1.2"]

log = logging.getLogger(__name__)


# noinspection PyDocstring
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


def json_load_file(url):
    # if '.json' isnt given, add it by default
    if not url.endswith('.json'):
        url += '.json'
    # requests can't handle file: scheme URLs
    fp = urllib.urlopen(url)
    try:
        return json.load(fp)
    finally:
        fp.close()


def json_load_url(http_client, url, headers):
    """Download and parse JSON from a URL.

    :param http_client: HTTP client interface.
    :type  http_client: http_client.HttpClient
    :param url: URL for JSON to parse
    :return: Parsed JSON dict
    """
    if is_file_scheme_uri(url):
        return json_load_file(url)
    else:
        request_params = {
            'method': 'GET',
            'url': url,
            'headers': headers,
        }
        req = http_client.start_request(request_params)
        resp = http_client.wait(req, timeout=None)
        return resp.json()


class Loader(object):
    """Abstraction for loading Swagger API's.

    :param http_client: HTTP client interface.
    :type  http_client: http_client.HttpClient
    :param processors: List of processors to apply to the API.
    :type  processors: list of SwaggerProcessor
    """

    def __init__(self, http_client, processors=None,
                 api_doc_request_headers=None):
        self.http_client = http_client
        self.api_doc_request_headers = api_doc_request_headers or {}
        if processors is None:
            processors = []
            # always go through the validation processor first
        # noinspection PyTypeChecker
        self.processors = [ValidationProcessor()] + processors

    def load_resource_listing(self, resources_url, base_url=None):
        """Load a resource listing, loading referenced API declarations.

        The following fields are added to the resource listing object model.
         * ['url'] = URL resource listing was loaded from
         * The ['apis'] array is modified according to load_api_declaration()

        The Loader's processors are applied to the fully loaded resource
        listing.

        :param resources_url:   File name for resources.json
        :param base_url:    Optional URL to be the base URL for finding API
                            declarations. If not specified, 'basePath' from the
                            resource listing is used.
        """

        # Load the resource listing
        resource_listing = json_load_url(
            self.http_client,
            resources_url,
            self.api_doc_request_headers,
        )
        self.pre_process_resource_listing(resource_listing)

        # Some extra data only known about at load time
        resource_listing[u'url'] = resources_url
        base_url = base_url if base_url else resources_url

        # Load the API declarations
        for api in resource_listing.get(u'apis'):
            self.load_api_declaration(base_url, api)

        # Now that the raw object model has been loaded, apply the processors
        self.process_resource_listing(resource_listing)
        return resource_listing

    def load_api_declaration(self, base_url, api_dict):
        """Load an API declaration file.

        api_dict is modified with the results of the load:
         * ['url'] = URL api declaration was loaded from
         * ['api_declaration'] = Parsed results of the load

        :param base_url: Base URL to load from
        :param api_dict: api object from resource listing.
        """
        api_dict[u'url'] = urlparse.urljoin(
            base_url + u'/', api_dict['path'].strip(u'/'))
        api_dict[u'api_declaration'] = json_load_url(
            self.http_client,
            api_dict[u'url'],
            self.api_doc_request_headers,
        )

    def pre_process_resource_listing(self, resources):
        """Apply pre-processors before loading resource listing.

        :param resources: Resource listing to process.
        """
        for processor in self.processors:
            processor.pre_apply(resources)

    def process_resource_listing(self, loaded_resources):
        """Apply processors to a resource listing.

        :param resources: Resource listing to process.
        """
        for processor in self.processors:
            processor.apply(loaded_resources)


def validate_required_fields(json, required_fields, context):
    """Checks a JSON object for a set of required fields.

    If any required field is missing, a SwaggerError is raised.

    :param json: JSON object to check.
    :param required_fields: List of required fields.
    :param context: Current context in the API.
    """
    missing_fields = [f for f in required_fields if f not in json]

    if missing_fields:
        raise SwaggerError(
            u"Missing fields: %s" % u', '.join(missing_fields), context)


def load_file(resource_listing_file, http_client=None, processors=None):
    """Loads a resource listing file, applying the given processors.

    :param http_client: HTTP client interface.
    :param resource_listing_file: File name for a resource listing.
    :param processors:  List of SwaggerProcessors to apply to the resulting
                        resource.
    :return: Processed object model from
    :raise: IOError: On error reading api-docs.
    """
    file_path = os.path.abspath(resource_listing_file)
    url = urlparse.urljoin(u'file:', urllib.pathname2url(file_path))
    # When loading from files, everything is relative to the resource listing
    dir_path = os.path.dirname(file_path)
    base_url = urlparse.urljoin(u'file:', urllib.pathname2url(dir_path))
    return load_url(url, http_client=http_client, processors=processors,
                    base_url=base_url)


def load_url(resource_listing_url, http_client=None, processors=None,
             base_url=None):
    """Loads a resource listing, applying the given processors.

    :param resource_listing_url: URL for a resource listing.
    :param http_client: HTTP client interface.
    :param processors:  List of SwaggerProcessors to apply to the resulting
                        resource.
    :param base_url:    Optional URL to be the base URL for finding API
                        declarations. If not specified, 'basePath' from the
                        resource listing is used.
    :return: Processed object model from
    :raise: IOError, URLError: On error reading api-docs.
    """
    if http_client is None:
        http_client = SynchronousHttpClient()

    loader = Loader(http_client=http_client, processors=processors)
    return loader.load_resource_listing(
        resource_listing_url, base_url=base_url)


def load_json(resource_listing, http_client=None, processors=None):
    """Process a resource listing that has already been parsed.

    :param resource_listing: Parsed resource listing.
    :type  resource_listing: dict
    :param http_client:
    :param processors:
    :return: Processed resource listing.
    """
    if http_client is None:
        http_client = SynchronousHttpClient()

    loader = Loader(http_client=http_client, processors=processors)
    loader.process_resource_listing(resource_listing)
    return resource_listing


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
        swagger_py_type = swagger_type.swagger_to_py_type(
            property_swagger_type)
        # Assign all property values specified in kwargs
        if property_name in arg_keys:
            property_value = kwargs[property_name]
            arg_keys.remove(property_name)
        else:
            # If not in kwargs, provide a default value to the type
            property_value = swagger_type.get_instance(swagger_py_type)
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
