#
# Copyright (c) 2013, Digium, Inc.
#

import swaggerpy
import os.path
import logging
import requests

from swaggerpy.processors import WebsocketProcessor, SwaggerProcessor

log = logging.getLogger(__name__)


class ClientProcessor(SwaggerProcessor):
    def process_resource_listing_api(self, resources, listing_api, context):
        name, ext = os.path.splitext(os.path.basename(listing_api.path))
        listing_api.name = name


class Resource(object):
    def __init__(self, resource):
        self.resource = resource
        decl = resource.api_declaration
        self.operations = dict(
            [(oper.nickname, self._build_operation(decl, api, oper))
             for api in decl.apis for oper in api.operations]
        )

    def __getattr__(self, name):
        """Access to resource objects.

        :param name: Name of the attribute to get.
        :rtype: Resource
        :return: Resource object.
        """
        op = self.operations.get(name)
        if not op:
            raise AttributeError("Resource '%s' has no operation '%s'" %
                                 (self.resource.path, name))
        return op

    def _build_operation(self, decl, api, operation):
        """Build an operation object
        """
        def invoke_oper(*args, **kwargs):
            log.info("%s(%r, %r)" % (operation.nickname, args, kwargs))
            method = operation.httpMethod
            uri = decl.basePath + api.path
            return requests.get(uri)
        return invoke_oper


class Resources(object):
    def __init__(self, api_docs):
        self.resources = dict(
            [(resource.name, Resource(resource))
             for resource in api_docs.apis])

    def __getattr__(self, name):
        """Access to resource objects.

        :param name: Name of the attribute to get.
        :rtype: Resource
        :return: Resource object.
        """
        return self.resources[name]


class SwaggerClient(object):
    """Client library for accessing a Swagger-documented RESTful service.
    """

    def __init__(self, discovery_url=None, resource_listing=None):
        """Create a SwaggerClient, either from a discovery URL or an already
        parsed resource listing.

        :type discovery_url: str
        :type resource_listing: dict
        :raise:
        """
        if not discovery_url and not resource_listing:
            raise ValueError("Missing discovery_url or api_docs")
        loader = swaggerpy.Loader([WebsocketProcessor(), ClientProcessor()])
        if resource_listing:
            self.api_docs = loader.process_resource_listing(resource_listing)
        else:
            self.api_docs = loader.load_resource_listing(discovery_url)
        self.apis = Resources(self.api_docs)
        """API access object"""
