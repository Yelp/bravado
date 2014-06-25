#
# Copyright (c) 2013, Digium, Inc.
#

"""Code for handling the base Swagger API model.
"""

import logging
import json
import os
import urllib
import urlparse

import swagger_type
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
                u"Unsupported Swagger version %s" % resources[u'swaggerVersion'],
                context)

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
                u"Unsupported Swagger version %s" % resource[u'swaggerVersion'],
                context)
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
        if operation.get(u'type') in swagger_type.CONTAINER_TYPES:
            validate_required_fields(operation, [u'items'], context)
            return validate_type_or_ref(operation[u'items'], model_ids)
        allowed_types = swagger_type.primitive_types() + \
            model_ids.get('model_ids') + ['void']
        if operation.get(u'type') not in allowed_types:
            raise SwaggerError("%s not in allowed ones: %s" % (
                operation.get(u'type'), allowed_types), context)

    def process_parameter(self, resources, resource, api, operation, parameter,
                          context, model_ids):
        # Assume 'type' is always necessary for any 'paramType'
        required_fields = [u'name', u'paramType', u'type']
        validate_required_fields(parameter, required_fields, context)
        if u'allowedValues' in parameter:
            raise SwaggerError(
                u"Field 'allowedValues' invalid; use 'allowableValues'",
                context)
        if parameter.get(u'type') in swagger_type.CONTAINER_TYPES:
            validate_required_fields(parameter, [u'items'], context)
            return validate_type_or_ref(parameter[u'items'], model_ids)
        allowed_types = swagger_type.primitive_types() + model_ids.get('model_ids')
        if parameter.get(u'type') not in allowed_types:
            raise SwaggerError("%s not in allowed types: %s" % (
                parameter.get(u'type'), allowed_types), context)

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
        validate_type_or_ref(prop, model_ids)


def json_load_url(http_client, url):
    """Download and parse JSON from a URL.

    :param http_client: HTTP client interface.
    :type  http_client: http_client.HttpClient
    :param url: URL for JSON to parse
    :return: Parsed JSON dict
    """
    scheme = urlparse.urlparse(url).scheme
    if scheme == u'file':
        # requests can't handle file: URLs
        fp = urllib.urlopen(url)
        try:
            return json.load(fp)
        finally:
            fp.close()
    else:
        resp = http_client.request(u'GET', url)
        resp.raise_for_status()
        return resp.json()


class Loader(object):
    """Abstraction for loading Swagger API's.

    :param http_client: HTTP client interface.
    :type  http_client: http_client.HttpClient
    :param processors: List of processors to apply to the API.
    :type  processors: list of SwaggerProcessor
    """

    def __init__(self, http_client, processors=None):
        self.http_client = http_client
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
        resource_listing = json_load_url(self.http_client, resources_url)
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
        path = api_dict.get(u'path').replace(u'{format}', u'json')
        # if loading via file and '.json' isnt given, add it by default
        if base_url.startswith('file:') and '.' not in path:
            path = path + '.json'
        api_dict[u'url'] = urlparse.urljoin(base_url + u'/', path.strip(u'/'))
        api_dict[u'api_declaration'] = json_load_url(
            self.http_client, api_dict[u'url'])

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


def create_model_type(model):
    """creates a dynamic model from the model data present in the json
       :param model: Resource Model json containing id, properties
       :type model: dict
       :returns: dynamic type created with attributes, docstrings attached
       :rtype: type
    """
    props = model['properties']
    name = str(model['id'])
    magic_methods = dict(
        # Define the docstring
        __doc__=create_model_docstring(props),
        # Make equality work for dict & type OR type & type
        __eq__=lambda self, other: compare(self, other),
        # Define the constructor for the type
        __init__=lambda self, **kwargs: set_props(self, **kwargs),
        # Define the str repr of the type
        __repr__=lambda self: create_model_repr(self))
    model_type = type(name, (object,), magic_methods)
    # Define a class variable to store types of its attributes
    setattr(model_type, '_swagger_types', swagger_type.get_swagger_types(props))
    # Define a class variable to store all required fields
    setattr(model_type, '_required', model.get('required'))
    return model_type


# ToDo: Check that no required fields are None if assigned by kwargs
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
        swagger_py_type = swagger_type.swagger_to_py_type(property_swagger_type)
        property_value = swagger_py_type() if swagger_py_type else None
        # Override any property values specified in kwargs
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

       Example:
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
    Result:
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
    return hasattr(second, '__dict__') and first.__dict__ == second.__dict__


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


def validate_type_or_ref(json, model_ids):
    """Validates that either type OR ref is present in the json

       :param json: dict to check whether type or ref is present
       :param model_ids: list of allowed $ref ids (all models)
    """
    if json.get(u'type') in swagger_type.CONTAINER_TYPES:
        return validate_type_or_ref(json[u'items'], model_ids)
    allowed_types = swagger_type.primitive_types()
    allowed_refs = model_ids.get('model_ids')
    if json.get(u'type') not in allowed_types and \
       json.get(u'$ref') not in allowed_refs:
        raise TypeError("%s not in allowed types: %s" % (
            json.get(u'type') or json.get(u'$ref'), allowed_types + allowed_refs))
