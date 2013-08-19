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

    def __init__(self):
        self.type_stack = []
        self.id_stack = []
        self.args = {'context': self}

    def __repr__(self):
        zipped = zip(self.type_stack, self.id_stack)
        strs = ["%s=%s" % (t, i) for (t, i) in zipped]
        return "ParsingContext(stack=%r)" % strs

    def is_empty(self):
        return not self.type_stack and not self.id_stack

    def push(self, obj_type, json, id_field):
        """Pushes a new self-identifying object into the context.

        @type obj_type: str
        @param obj_type: Specifies type of object json represents
        @type json: Jsonified
        @param json: Current Jsonified object.
        @type id_field: str
        @param id_field: Field name in json that identifies it.
        """
        if id_field not in json.get_field_names():
            raise SwaggerError("Missing id_field: %s" % id_field, self)
        self.push_str(obj_type, json, str(json[id_field]))

    def push_str(self, obj_type, json, id_string):
        """Pushes a new object into the context.

        @type obj_type: str
        @param obj_type: Specifies type of object json represents
        @type json: Jsonified
        @param json: Current Jsonified object.
        @type id_string: str
        @param id_string: Identifier of the given json.
        """
        self.type_stack.append(obj_type)
        self.id_stack.append(id_string)
        self.args[obj_type] = json

    def pop(self):
        """Pops the most recent object out of the context
        """
        self.type_stack.pop()
        del self.args[self.type_stack.pop()]


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


class SwaggerProcessor(object):
    """Post processing interface for Swagger API's.

    This processor can add fields to model objects for additional
    information to use in the templates.
    """

    def apply(self, resources):
        context = ParsingContext()
        context.push_str('resources', resources, resources.file)
        self.process_resource_listing(**context.args)
        for api in resources.apis:
            context.push('listing_api', api, 'path')
            self.process_resource_listing_api(**context.args)
            context.pop()

            context.push_str('api_declaration', api.api_declaration, api.file)
            self.process_api_declaration(**context.args)
            for resource_api in api.api_declaration.apis:
                context.push('resource_api', resource_api, 'path')
                self.process_resource_api(**context.args)
                for operation in resource_api.operations:
                    context.push('operation', operation, 'nickname')
                    self.process_operation(**context.args)
                    for parameter in operation.parameters:
                        context.push('parameter', parameter, 'name')
                        self.process_parameter(**context.args)
                        context.pop()
                    for response in operation.error_responses:
                        context.push('error_response', response, 'code')
                        self.process_error_response(**context.args)
                        context.pop()
                    context.pop()
                context.pop()
            for (model_name, model) in api.api_declaration.models:
                context.push('model', model, 'id')
                self.process_model(**context.args)
                if model_name != model.id:
                    raise SwaggerError("Model id doesn't match name", context)
                for (prop_name, prop) in model.properties:
                    context.push_str('property', prop, prop_name)
                    prop.name = prop_name
                    self.process_property(**context.args)
                    context.pop()
            context.pop()
        context.pop()
        assert context.is_empty()

    def process_resource_listing(self, resources, context):
        """Post process a resources.json object.

        @param resources: ResourceApi object.
        @type context: ParsingContext
        @param context: Current context in the API.
        """
        pass

    def process_resource_listing_api(self, resources, listing_api, context):
        """Post process entries in a resource.json's api array.

        @param resources: Resource listing object
        @param listing_api: ResourceApi object.
        @type context: ParsingContext
        @param context: Current context in the API.
        """
        pass

    def process_api_declaration(self, resources, api_declaration, context):
        """Post process a resource object.

        This is parsed from a .json file reference by a resource listing's
        'api' array.

        @param api_declaration: resource object.
        @type context: ParsingContext
        @param context: Current context in the API.
        """
        pass

    def process_resource_api(self, resources, api_declaration, api, context):
        """Post process entries in a resource's api array

        @param api: API object
        @type context: ParsingContext
        @param context: Current context in the API.
        """
        pass

    def process_operation(self, resources, resource, api, operation, context):
        """Post process an operation on an api.

        @param operation: Operation object.
        @type context: ParsingContext
        @param context: Current context in the API.
        """
        pass

    def process_parameter(self, resources, resource, api, operation, parameter,
                          context):
        """Post process a parameter on an operation.

        @param parameter: Parameter object.
        @type context: ParsingContext
        @param context: Current context in the API.
        """
        pass

    def process_error_response(self, resources, resource, api, operation,
                               error_response, context):
        """Post process an errorResponse on an operation.

        @param error_response: Response object.
        @type context: ParsingContext
        @param context: Current context in the API.
        """
        pass

    def process_model(self, resources, resource, model, context):
        """Post process a model from a resources model dictionary.

        @param model: Model object.
        @type context: ParsingContext
        @param context: Current context in the API.
        """
        pass

    def process_property(self, resources, resource, model, prop, context):
        """Post process a property from a model.

        @param prop: Property object.
        @type context: ParsingContext
        @param context: Current context in the API.
        """
        pass

    def process_type(self, swagger_type, context):
        """Post process a type.

        @param swagger_type: ResourceListing object.
        @type context: ParsingContext
        @param context: Current context in the API.
        """
        pass


class DefaultProcessor(SwaggerProcessor):
    def process_resource_listing(self, resources, context):
        required_fields = ['apiVersion', 'basePath', 'apis', 'swaggerVersion']
        validate_required_fields(resources, required_fields, context)

        if not resources.swaggerVersion in SWAGGER_VERSIONS:
            raise SwaggerError(
                "Unsupported Swagger version %s" % resources.swaggerVersion,
                context)

        for api in resources.apis:
            self.process_resource_listing_api(resources, api, context)

    def process_resource_listing_api(self, resources, listing_api, context):
        context = context.next_stack(listing_api, 'path')
        validate_required_fields(listing_api, ['path', 'description'], context)

        if not listing_api.path.startswith("/"):
            raise SwaggerError("Path must start with /", context)

    def process_api_declaration(self, resources, api_declaration, context):
        required_fields = [
            'swaggerVersion', 'apiVersion', 'basePath', 'resourcePath', 'apis',
            'models'
        ]
        validate_required_fields(api_declaration, required_fields, context)

    def process_resource_api(self, resources, api_declaration, api, context):
        pass

    def process_operation(self, resources, resource, api, operation, context):
        pass

    def process_parameter(self, resources, resource, api, operation, parameter,
                          context):
        pass

    def process_error_response(self, resources, resource, api, operation,
                               response, context):
        pass

    def process_model(self, resources, resource, model, context):
        pass

    def process_property(self, resources, resource, model, prop, context):
        pass

    def process_type(self, swagger_type, context):
        pass


class Loader(object):
    def __init__(self, processors=None):
        if processors is None:
            processors = []
        self.processors = processors

    def load_resource_listing(self, resources_file):
        """Load a resource listing.

        @param resources_file: File name for resources.json
        """

        # Load the resource listing
        with open(resources_file) as fp:
            resources = Jsonified(json.load(fp))

        # Some extra data only known about at load time
        resources.file = resources_file
        resources.base_dir = os.path.dirname(resources_file)

        # Load the API declarations
        for api in resources.apis:
            self.load_api_declaration(resources, api)

        # Now that the raw object model has been loaded, apply the processors
        for processor in self.processors:
            processor.apply(resources)

        return resources

    def load_api_declaration(self, resources, api):
        api.file = (resources.base_dir + api.path).replace('{format}', 'json')
        with open(api.file) as fp:
            print "Adding api_declaration to %r" % api
            api.api_declaration = Jsonified(json.load(fp))
            print " done: %r" % api


def validate_required_fields(json, required_fields, context):
    """Checks a JSON object for a set of required fields.

    If any required field is missing, a SwaggerError is raised.

    @type json: Jsonified
    @param json: JSON object to check.
    @param required_fields: List of required fields.
    @param context: Current context in the API.
    """
    missing_fields = [f for f in required_fields if not f in json.get_field_names()]

    if missing_fields:
        raise SwaggerError(
            "Missing fields: %s" % ', '.join(missing_fields), context)
