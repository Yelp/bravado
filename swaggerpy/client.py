#
# Copyright (c) 2013, Digium, Inc.
#

"""Swagger client library.
"""

import logging
import os.path
import re
import urllib
import swaggerpy

from swaggerpy.http_client import SynchronousHttpClient
from swaggerpy.processors import WebsocketProcessor, SwaggerProcessor

log = logging.getLogger(__name__)


class ClientProcessor(SwaggerProcessor):
    """Enriches swagger models for client processing.
    """

    def process_resource_listing_api(self, resources, listing_api, context):
        """Add name to listing_api.

        :param resources: Resource listing object
        :param listing_api: ResourceApi object.
        :type context: ParsingContext
        :param context: Current context in the API.
        """
        name, ext = os.path.splitext(os.path.basename(listing_api['path']))
        listing_api['name'] = name


class Operation(object):
    """Operation object.
    """

    def __init__(self, uri, operation, http_client):
        self.uri = uri
        self.json = operation
        self.http_client = http_client

    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__, self.json['nickname'])

    def __call__(self, **kwargs):
        """Invoke ARI operation.

        :param kwargs: ARI operation arguments.
        :return: Implementation specific response or WebSocket connection
        """
        log.info("%s?%r" % (self.json['nickname'], urllib.urlencode(kwargs)))
        method = self.json['httpMethod']
        uri = self.uri
        params = {}
        for param in self.json.get('parameters', []):
            pname = param['name']
            value = kwargs.get(pname)
            # Turn list params into comma separated values
            if isinstance(value, list):
                value = ",".join(value)

            if value:
                if param['paramType'] == 'path':
                    uri = uri.replace('{%s}' % pname, str(value))
                elif param['paramType'] == 'query':
                    params[pname] = value
                else:
                    raise AssertionError(
                        "Unsupported paramType %s" %
                        param.paramType)
                del kwargs[pname]
            else:
                if param['required']:
                    raise TypeError(
                        "Missing required parameter '%s' for '%s'" %
                        (pname, self.json['nickname']))
        if kwargs:
            raise TypeError("'%s' does not have parameters %r" %
                            (self.json['nickname'], kwargs.keys()))

        log.info("%s %s(%r)", method, uri, params)
        if self.json['is_websocket']:
            # Fix up http: URLs
            uri = re.sub('^http', "ws", uri)
            return self.http_client.ws_connect(uri, params=params)
        else:
            return self.http_client.request(
                method, uri, params=params)


class Resource(object):
    """Swagger resource, described in an API declaration.

    :param resource: Resource model
    :param http_client: HTTP client API
    """

    def __init__(self, resource, http_client):
        log.debug("Building resource '%s'" % resource['name'])
        self.json = resource
        decl = resource['api_declaration']
        self.http_client = http_client
        self.operations = {
            oper['nickname']: self._build_operation(decl, api, oper)
            for api in decl['apis']
            for oper in api['operations']}

    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__, self.json['name'])

    def __getattr__(self, item):
        """Promote operations to be object fields.

        :param item: Name of the attribute to get.
        :rtype: Resource
        :return: Resource object.
        """
        op = self.get_operation(item)
        if not op:
            raise AttributeError("Resource '%s' has no operation '%s'" %
                                 (self.get_name(), item))
        return op

    def get_operation(self, name):
        """Gets the operation with the given nickname.

        :param name: Nickname of the operation.
        :rtype:  Operation
        :return: Operation, or None if not found.
        """
        return self.operations.get(name)

    def get_name(self):
        """Returns the name of this resource.

        Name is derived from the filename of the API declaration.

        :return: Resource name.
        """
        return self.json.get('name')

    def _build_operation(self, decl, api, operation):
        """Build an operation object

        :param decl: API declaration.
        :param api: API entry.
        :param operation: Operation.
        """
        log.debug("Building operation %s.%s" % (
            self.get_name(), operation['nickname']))
        uri = decl['basePath'] + api['path']
        return Operation(uri, operation, self.http_client)


class SwaggerClient(object):
    """Client object for accessing a Swagger-documented RESTful service.

    :param url_or_resource: Either the parsed resource listing+API decls, or
                            its URL.
    :type url_or_resource: dict or str
    :param http_client: HTTP client API
    :type  http_client: HttpClient
    """

    def __init__(self, url_or_resource, http_client=None):
        if not http_client:
            http_client = SynchronousHttpClient()
        self.http_client = http_client

        loader = swaggerpy.Loader(
            http_client, [WebsocketProcessor(), ClientProcessor()])

        if isinstance(url_or_resource, str):
            log.debug("Loading from %s" % url_or_resource)
            self.api_docs = loader.load_resource_listing(url_or_resource)
        else:
            log.debug("Loading from %s" % url_or_resource.get('basePath'))
            self.api_docs = url_or_resource
            loader.process_resource_listing(self.api_docs)

        self.resources = {
            resource['name']: Resource(resource, http_client)
            for resource in self.api_docs['apis']}

    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__, self.api_docs['basePath'])

    def __getattr__(self, item):
        """Promote resource objects to be client fields.

        :param item: Name of the attribute to get.
        :return: Resource object.
        """
        resource = self.get_resource(item)
        if not resource:
            raise AttributeError("API has no resource '%s'" % item)
        return resource

    def close(self):
        """Close the SwaggerClient, and underlying resources.
        """
        self.http_client.close()

    def get_resource(self, name):
        """Gets a Swagger resource by name.

        :param name: Name of the resource to get
        :rtype: Resource
        :return: Resource, or None if not found.
        """
        return self.resources.get(name)
