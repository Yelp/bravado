#
# Copyright (c) 2013, Digium, Inc.
#

import json
import os

from jsonify import Jsonified

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


class ParsingContext(object):
    """Context information for parsing.

    This object is immutable. To change contexts (like adding an item to the
    stack), use the next() and next_stack() functions to build a new one.
    """

    def __init__(self, swagger_version, stack):
        self.__swagger_version = swagger_version
        self.__stack = stack

    def __repr__(self):
        return "ParsingContext(swagger_version=%s, stack=%s)" % (
            self.swagger_version, self.stack)

    def get_swagger_version(self):
        return self.__swagger_version

    def get_stack(self):
        return self.__stack

    swagger_version = property(get_swagger_version)

    stack = property(get_stack)

    def version_less_than(self, ver):
        return compare_versions(self.swagger_version, ver) < 0

    def next_stack(self, json, id_field):
        """Returns a new item pushed to the stack.

        @param json: Current JSON object.
        @param id_field: Field identifying this object.
        @return New context with additional item in the stack.
        """
        if not id_field in json:
            raise SwaggerError("Missing id_field: %s" % id_field, self)
        new_stack = self.stack + ['%s=%s' % (id_field, str(json[id_field]))]
        return ParsingContext(self.swagger_version, new_stack)

    def next(self, version=None, stack=None):
        if version is None:
            version = self.swagger_version
        if stack is None:
            stack = self.stack
        return ParsingContext(version, stack)


class SwaggerError(Exception):
    """Raised when an error is encountered mapping the JSON objects into the
    model.
    """

    def __init__(self, msg, context, cause=None):
        """Ctor.

        @param msg: String message for the error.
        @param context: ParsingContext object
        @param cause: Optional exception that caused this one.
        """
        super(Exception, self).__init__(msg, context, cause)


class SwaggerPostProcessor(object):
    """Post processing interface for model objects.

    This processor can add fields to model objects for additional
    information to use in the templates.

    """

    def process_resource_listing(self, resources, context):
        """Post process a resources.json object.

        @param resources: ResourceApi object.
        @param context: Current context in the API.
        """
        pass

    def process_resource_listing_api(self, resource_api, context):
        """Post process entries in a resource.json's api array.

        @param resource_api: ResourceApi object.
        @param context: Current context in the API.
        """
        pass

    def process_api_declaration(self, resource, context):
        """Post process a resource object.

        This is parsed from a .json file reference by a resource listing's 'api'
        array.

        @param resource: resource object.
        @param context: Current context in the API.
        """
        pass

    def process_resource_api(self, api, context):
        """Post process entries in a resource's api array

        @param api: API object
        @param context: Current context in the API.
        """
        pass

    def process_operation(self, operation, context):
        """Post process an operation on an api.

        @param operation: Operation object.
        @param context: Current context in the API.
        """
        pass

    def process_parameter(self, parameter, context):
        """Post process a parameter on an operation.

        @param parameter: Parameter object.
        @param context: Current context in the API.
        """
        pass

    def process_error_response(self, response, context):
        """Post process an errorResponse on an operation.

        @param response: Parameter object.
        @param context: Current context in the API.
        """
        pass

    def process_model(self, model, context):
        """Post process a model from a resources model dictionary.

        @param model: Model object.
        @param context: Current context in the API.
        """
        pass

    def process_property(self, prop, context):
        """Post process a property from a model.

        @param prop: Property object.
        @param context: Current context in the API.
        """
        pass

    def process_type(self, swagger_type, context):
        """Post process a type.

        @param swagger_type: ResourceListing object.
        @param context: Current context in the API.
        """
        pass


def load_resource_listing(resources_file, processor):
    """Load a resource listing.

    @param resources_file: File name for resources.json
    @type processor: SwaggerPostProcessor
    @param processor: Custom SwaggerPostProcessor.
    """
    context = ParsingContext(None, [resources_file])
    with open(resources_file) as fp:
        resources = Jsonified(json.load(fp))
        resources.file = resources_file
        resources.base_dir = os.path.dirname(resources_file)
        return process_resource_listing(resources, processor,
                                        context)


def process_resource_listing(resources, processor, context):
    """Post process entries in a resource's api array

    @param resources: Resources object.
    @type processor: SwaggerPostProcessor
    @param processor: Custom SwaggerPostProcessor.
    @type context: ParsingContext
    @param context: Current context in the API.

    """
    required_fields = ['apiVersion', 'basePath', 'apis', 'swaggerVersion']
    validate_required_fields(resources, required_fields, context)

    if not resources.swaggerVersion in SWAGGER_VERSIONS:
        raise SwaggerError(
            "Unsupported Swagger version %s" % resources.swaggerVersion,
            context)

    for api in resources.apis:
        process_resource_listing_api(api, processor, resources.base_dir,
                                     context)
    processor.process_resource_listing(resources, context)
    return resources


def process_resource_listing_api(api, processor, base_dir, context):
    """Post process entries in a resource's api array

    @param api: API object.
    @type processor: SwaggerPostProcessor
    @param processor: Custom SwaggerPostProcessor.
    @type context: ParsingContext
    @param context: Current context in the API.

    """
    context = context.next_stack(api, 'path')
    validate_required_fields(api, ['path', 'description'], context)

    if not api.path.startswith("/"):
        raise SwaggerError("Path must start with /", context)

    api.file = (base_dir + api.path).replace('{format}', 'json')

    api.api_declaration = load_api_declaration(api.file, processor)

    processor.process_resource_api(api, context)
    return api


def load_api_declaration(api_file, processor):
    context = ParsingContext(None, [api_file])
    with open(api_file) as fp:
        api_declaration = Jsonified(json.load(fp))
        api_declaration.file = api_file
        process_api_declaration(api_declaration, processor, context)
        return api_declaration


def process_api_declaration(api_declaration, processor, context):
    """Post process entries in a resource's api array

    @param api_declaration: API declaration object.
    @type processor: SwaggerPostProcessor
    @param processor: Custom SwaggerPostProcessor.
    @type context: ParsingContext
    @param context: Current context in the API.
    """
    required_fields = [
        'swaggerVersion', 'apiVersion', 'basePath', 'resourcePath', 'apis',
        'models'
    ]
    validate_required_fields(api_declaration, required_fields, context)

    for api in api_declaration.apis:
        process_resource_api(api, processor, context)

    # Extract models from object to an array, for better mustache-ness
    api_declaration.models = [
        process_model(model, model_id, processor, context)
        for (model_id, model) in api_declaration.models
    ]

    processor.process_api_declaration(api_declaration, context)
    return api_declaration


def process_resource_api(api, processor, context):
    """Post process entries in a resource's api array

    @param api: API object.
    @type processor: SwaggerPostProcessor
    @param processor: Custom SwaggerPostProcessor.
    @type context: ParsingContext
    @param context: Current context in the API.

    """
    pass


def process_operation(operation, processor, context):
    """Post process an operation on an api.

    @param operation: Operation object.
    @type processor: SwaggerPostProcessor
    @param processor: Custom SwaggerPostProcessor.
    @type context: ParsingContext
    @param context: Current context in the API.
    """
    pass


def process_parameter(parameter, processor, context):
    """Post process a parameter on an operation.

    @param parameter: Parameter object.
    @type processor: SwaggerPostProcessor
    @param processor: Custom SwaggerPostProcessor.
    @type context: ParsingContext
    @param context: Current context in the API.
    """
    pass


def process_error_response(response, processor, context):
    """Post process an errorResponse on an operation.

    @param response: Parameter object.
    @type processor: SwaggerPostProcessor
    @param processor: Custom SwaggerPostProcessor.
    @type context: ParsingContext
    @param context: Current context in the API.
    """
    pass


def process_model(model, model_id, processor, context):
    """Post process a model from a resources model dictionary.

    @param model: Model object.
    @type processor: SwaggerPostProcessor
    @param processor: Custom SwaggerPostProcessor.
    @type context: ParsingContext
    @param context: Current context in the API.
    """
    pass


def process_property(prop, processor, context):
    """Post process a property from a model.

    @param prop: Property object.
    @type processor: SwaggerPostProcessor
    @param processor: Custom SwaggerPostProcessor.
    @type context: ParsingContext
    @param context: Current context in the API.
    """
    pass


def process_type(swagger_type, processor, context):
    """Post process a type.

    @param swagger_type: ResourceListing object.
    @type processor: SwaggerPostProcessor
    @param processor: Custom SwaggerPostProcessor.
    @type context: ParsingContext
    @param context: Current context in the API.
    """
    pass


def validate_required_fields(json, required_fields, context):
    """Checks a JSON object for a set of required fields.

    If any required field is missing, a SwaggerError is raised.

    @param json: JSON object to check.
    @param required_fields: List of required fields.
    @param context: Current context in the API.
    """
    missing_fields = [f for f in required_fields if not f in json]

    if missing_fields:
        raise SwaggerError(
            "Missing fields: %s" % ', '.join(missing_fields), context)
