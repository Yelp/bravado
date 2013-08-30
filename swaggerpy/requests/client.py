#
# Copyright (c) 2013, Digium, Inc.
#

import swaggerpy
import os.path
import logging

from swaggerpy.processors import WebsocketProcessor, SwaggerProcessor

log = logging.getLogger(__name__)


class ClientProcessor(SwaggerProcessor):
    def process_resource_listing_api(self, resources, listing_api, context):
        name, ext = os.path.splitext(os.path.basename(listing_api.path))
        listing_api.name = name


class Resource(object):
    def __init__(self, resource):
        decl = resource.api_declaration
        for api in decl.apis:
            for operation in api.operations:
                def invoke_oper(*args, **kwargs):
                    method = operation.httpMethod
                    uri = decl.basePath + api.path

                setattr(self, operation.nickname, invoke_oper)


class Resources(object):
    def __init__(self, api_docs):
        for resource in api_docs.apis:
            setattr(self, resource.name, Resource(resource))


class SwaggerClient(object):
    def __init__(self, discovery_url=None, resource_listing=None):
        if not discovery_url and not resource_listing:
            raise ValueError("Missing discovery_url or api_docs")
        loader = swaggerpy.Loader([WebsocketProcessor(), ClientProcessor()])
        if resource_listing:
            self.api_docs = loader.process_resource_listing(resource_listing)
        else:
            self.api_docs = loader.load_resource_listing(discovery_url)
        self.apis = Resources(self.api_docs)
