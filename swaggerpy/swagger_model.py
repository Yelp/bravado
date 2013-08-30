#
# Copyright (c) 2013, Digium, Inc.
#

"""Code for handling the base Swagger API model.
"""

import json
import os
import urllib
import urllib2
import urlparse

from swaggerpy.jsonify import jsonify
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


def compare_versions(lhs, rhs):
    """Performs a lexicographical comparison between two version numbers.

    This properly handles simple major.minor.whatever.sure.why.not version
    numbers, but fails miserably if there's any letters in there.

    For reference:
      1.0 == 1.0
      1.0 < 1.0.1
      1.2 < 1.10

    @param lhs Left hand side of the comparison
    @param rhs Right hand side of the comparison
    @return  < 0 if lhs  < rhs
    @return == 0 if lhs == rhs
    @return  > 0 if lhs  > rhs
    """
    lhs = [int(v) for v in lhs.split('.')]
    rhs = [int(v) for v in rhs.split('.')]
    return cmp(lhs, rhs)


class ValidationProcessor(SwaggerProcessor):
    """A processor that validates the Swagger model.
    """
    def process_resource_listing(self, resources, context):
        required_fields = ['basePath', 'apis', 'swaggerVersion']
        validate_required_fields(resources, required_fields, context)

        if not resources.swaggerVersion in SWAGGER_VERSIONS:
            raise SwaggerError(
                "Unsupported Swagger version %s" % resources.swaggerVersion,
                context)

    def process_resource_listing_api(self, resources, listing_api, context):
        validate_required_fields(listing_api, ['path', 'description'], context)

        if not listing_api.path.startswith("/"):
            raise SwaggerError("Path must start with /", context)

    def process_api_declaration(self, resources, resource, context):
        required_fields = [
            'swaggerVersion', 'basePath', 'resourcePath', 'apis',
            'models'
        ]
        validate_required_fields(resource, required_fields, context)
        # Check model name and id consistency
        for (model_name, model) in resource.models:
            if model_name != model.id:
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
        required_fields = ['name', 'dataType']
        validate_required_fields(parameter, required_fields, context)
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
        for (prop_name, prop) in model.properties:
            prop.name = prop_name

    def process_property(self, resources, resource, model, prop,
                         context):
        required_fields = ['type']
        validate_required_fields(prop, required_fields, context)


def json_load_url(opener, url):
    """Download and parse JSON from a URL, wrapping in a Jsonify.

    @type opener: urllib2.OpenerDirector
    @param opener: Opener for requesting JSON.
    @param url: URL for JSON to parse
    @return: Parse JSON dict
    """
    fp = opener.open(url)
    try:
        return json.load(fp)
    finally:
        fp.close()


class Loader(object):
    def __init__(self, processors=None):
        if processors is None:
            processors = []
        # always go through the validation processor first
        self.processors = [ValidationProcessor()]
        self.processors.extend(processors)

    def load_resource_listing(self, resources_url, opener=None, base_url=None):
        """Load a resource listing.

        @param resources_url:   File name for resources.json
        @param base_url:    Optional URL to be the base URL for finding API
                            declarations. If not specified, 'basePath' from the
                            resource listing is used.
        """

        if not opener:
            opener = urllib2.build_opener()

        # Load the resource listing
        resource_listing_dict = json_load_url(opener, resources_url)

        # Some extra data only known about at load time
        resource_listing_dict['url'] = resources_url
        if not base_url:
            base_url = resource_listing_dict.basePath

        # Load the API declarations
        for api in resource_listing_dict.get('apis'):
            self.load_api_declaration(opener, base_url, api)

        # Now that the raw object model has been loaded, apply the processors
        resource_listing_json = self.process_resource_listing(
            resource_listing_dict)

        return resource_listing_json

    def load_api_declaration(self, opener, base_url, api_dict):
        path = api_dict.get('path').replace('{format}', 'json')
        api_dict['url'] = urlparse.urljoin(base_url + '/', path.strip('/'))
        api_dict['api_declaration'] = json_load_url(opener, api_dict['url'])

    def process_resource_listing(self, resources):
        jsonified = jsonify(resources)
        for processor in self.processors:
            processor.apply(jsonified)
        return jsonified


def validate_required_fields(json, required_fields, context):
    """Checks a JSON object for a set of required fields.

    If any required field is missing, a SwaggerError is raised.

    @type json: Jsonified
    @param json: JSON object to check.
    @param required_fields: List of required fields.
    @param context: Current context in the API.
    """
    missing_fields = [f for f in required_fields
                      if not f in json.get_field_names()]

    if missing_fields:
        raise SwaggerError(
            "Missing fields: %s" % ', '.join(missing_fields), context)


def load_file(resource_listing_file, processors=None, opener=None):
    """Loads a resource listing file, applying the given processors.

    @param resource_listing_file: File name for a resource listing.
    @param processors:  List of SwaggerProcessors to apply to the resulting
                        resource.
    @param opener:  Optional urllib2 opener for fetching API docs.
    @return: Processed object model from
    @raise IOError: On error reading api-docs.
    """
    file_path = os.path.abspath(resource_listing_file)
    url = urlparse.urljoin('file:', urllib.pathname2url(file_path))
    # When loading from files, everything is relative to the resource listing
    dir_path = os.path.dirname(file_path)
    base_url = urlparse.urljoin('file:', urllib.pathname2url(dir_path))
    return load_url(url, processors, opener=opener, base_url=base_url)


def load_url(resource_listing_url, processors=None, opener=None,
             base_url=None):
    """Loads a resource listing, applying the given processors.

    @param resource_listing_url: URL for a resource listing.
    @param processors:  List of SwaggerProcessors to apply to the resulting
                        resource.
    @param opener:  Optional urllib2 opener for fetching API docs.
    @param base_url:    Optional URL to be the base URL for finding API
                        declarations. If not specified, 'basePath' from the
                        resource listing is used.
    @return: Processed object model from
    @raise IOError, URLError: On error reading api-docs.
    """
    loader = Loader(processors)
    return loader.load_resource_listing(
        resource_listing_url, opener=opener, base_url=base_url)


def load_json(resource_listing, processors=None):
    loader = Loader(processors)
    return loader.process_resource_listing(resource_listing)
