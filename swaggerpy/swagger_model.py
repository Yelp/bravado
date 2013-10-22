#
# Copyright (c) 2013, Digium, Inc.
#

"""Code for handling the base Swagger API model.
"""

import json
import os
import urllib
import urlparse

from swaggerpy.http_client import SynchronousHttpClient
from swaggerpy.processors import SwaggerProcessor, SwaggerError

SWAGGER_VERSIONS = ["1.1", "1.2"]

SWAGGER_PRIMITIVES = [
    'void',
    'string',
    'boolean',
    'number',
    'int',
    'long',
    'double',
    'float',
    'Date',
]


# noinspection PyDocstring
class ValidationProcessor(SwaggerProcessor):
    """A processor that validates the Swagger model.
    """

    def process_resource_listing(self, resources, context):
        required_fields = ['basePath', 'apis', 'swaggerVersion']
        validate_required_fields(resources, required_fields, context)

        if not resources['swaggerVersion'] in SWAGGER_VERSIONS:
            raise SwaggerError(
                "Unsupported Swagger version %s" % resources.swaggerVersion,
                context)

    def process_resource_listing_api(self, resources, listing_api, context):
        validate_required_fields(listing_api, ['path', 'description'], context)

        if not listing_api['path'].startswith("/"):
            raise SwaggerError("Path must start with /", context)

    def process_api_declaration(self, resources, resource, context):
        required_fields = [
            'swaggerVersion', 'basePath', 'resourcePath', 'apis',
            'models'
        ]
        validate_required_fields(resource, required_fields, context)
        # Check model name and id consistency
        for (model_name, model) in resource['models'].items():
            if model_name != model['id']:
                raise SwaggerError("Model id doesn't match name", context)
                # Convert models dict to list

    def process_resource_api(self, resources, resource, api, context):
        required_fields = ['path', 'operations']
        validate_required_fields(api, required_fields, context)

    def process_operation(self, resources, resource, api, operation, context):
        required_fields = ['httpMethod', 'nickname']
        validate_required_fields(operation, required_fields, context)

    def process_parameter(self, resources, resource, api, operation, parameter,
                          context):
        required_fields = ['name', 'paramType']
        validate_required_fields(parameter, required_fields, context)
        if parameter['paramType'] == 'path':
            # special handling for path parameters
            parameter['required'] = True
            parameter['dataType'] = 'string'
        else:
            # dataType is required for non-path parameters
            validate_required_fields(parameter, ['dataType'], context)
        if 'allowedValues' in parameter:
            raise SwaggerError(
                "Field 'allowedValues' invalid; use 'allowableValues'",
                context)

    def process_error_response(self, resources, resource, api, operation,
                               error_response, context):
        required_fields = ['code', 'reason']
        validate_required_fields(error_response, required_fields, context)

    def process_model(self, resources, resource, model, context):
        required_fields = ['id', 'properties']
        validate_required_fields(model, required_fields, context)
        # Move property field name into the object
        for (prop_name, prop) in model['properties'].items():
            prop['name'] = prop_name

    def process_property(self, resources, resource, model, prop,
                         context):
        required_fields = ['type']
        validate_required_fields(prop, required_fields, context)


def json_load_url(http_client, url):
    """Download and parse JSON from a URL.

    :param http_client: HTTP client interface.
    :type  http_client: http_client.HttpClient
    :param url: URL for JSON to parse
    :return: Parsed JSON dict
    """
    scheme = urlparse.urlparse(url).scheme
    if scheme == 'file':
        # requests can't handle file: URLs
        fp = urllib.urlopen(url)
        try:
            return json.load(fp)
        finally:
            fp.close()
    else:
        resp = http_client.request('GET', url)
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

        # Some extra data only known about at load time
        resource_listing['url'] = resources_url
        if not base_url:
            base_url = resource_listing.get('basePath')

        # Load the API declarations
        for api in resource_listing.get('apis'):
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
        path = api_dict.get('path').replace('{format}', 'json')
        api_dict['url'] = urlparse.urljoin(base_url + '/', path.strip('/'))
        api_dict['api_declaration'] = json_load_url(
            self.http_client, api_dict['url'])

    def process_resource_listing(self, resources):
        """Apply processors to a resource listing.

        :param resources: Resource listing to process.
        """
        for processor in self.processors:
            processor.apply(resources)


def validate_required_fields(json, required_fields, context):
    """Checks a JSON object for a set of required fields.

    If any required field is missing, a SwaggerError is raised.

    :param json: JSON object to check.
    :param required_fields: List of required fields.
    :param context: Current context in the API.
    """
    missing_fields = [f for f in required_fields if not f in json]

    if missing_fields:
        raise SwaggerError(
            "Missing fields: %s" % ', '.join(missing_fields), context)


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
    url = urlparse.urljoin('file:', urllib.pathname2url(file_path))
    # When loading from files, everything is relative to the resource listing
    dir_path = os.path.dirname(file_path)
    base_url = urlparse.urljoin('file:', urllib.pathname2url(dir_path))
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
