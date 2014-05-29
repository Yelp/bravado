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
from urlparse import urlparse
from swaggerpy.http_client import SynchronousHttpClient
from swaggerpy.processors import WebsocketProcessor, SwaggerProcessor

log = logging.getLogger(__name__)


class ClientProcessor(SwaggerProcessor):
    """Enriches swagger models for client processing.
        Modified for Python 2.6 and Swagger 1.2
    """

    def process_resource_listing_api(self, resources, listing_api, context):
        """Add name to listing_api.

        :param resources: Resource listing object
        :param listing_api: ResourceApi object.
        :type context: ParsingContext
        :param context: Current context in the API.
        """
        name, ext = os.path.splitext(os.path.basename(listing_api[u'path']))
        log.debug("API name is %s", name)
        listing_api[u'name'] = name


class Operation(object):
    """Operation object.
    """

    def __init__(self, uri, operation, http_client):
        self.uri = uri
        self.json = operation
        self.http_client = http_client

    def __repr__(self):
        return u"%s(%s)" % (self.__class__.__name__, self.json[u'nickname'])

    def __call__(self, **kwargs):
        """Invoke ARI operation.

        :param kwargs: ARI operation arguments.
        :return: Implementation specific response or WebSocket connection
        """
        log.info(u"%s?%r" % (self.json[u'nickname'], urllib.urlencode(kwargs)))
        method = self.json[u'method']
        uri = self.uri
        params = {}
        for param in self.json.get(u'parameters', []):
            pname = param[u'name']
            value = kwargs.get(pname)
            # Turn list params into comma separated values
            if isinstance(value, list):
                value = u",".join(value)

            if value:
                if param[u'paramType'] == u'path':
                    uri = uri.replace(u'{%s}' % pname, unicode(value))
                elif param[u'paramType'] == u'query':
                    params[pname] = value
                else:
                    raise AssertionError(
                        u"Unsupported paramType %s" %
                        param.paramType)
                del kwargs[pname]
            else:
                if param.get(u'required'):
                    raise TypeError(
                        u"Missing required parameter '%s' for '%s'" %
                        (pname, self.json[u'nickname']))
        if kwargs:
            raise TypeError(u"'%s' does not have parameters %r" %
                            (self.json[u'nickname'], kwargs.keys()))

        log.info(u"%s %s(%r)", method, uri, params)
        if self.json[u'is_websocket']:
            # Fix up http: URLs
            uri = re.sub(u'^http', u"ws", uri)
            return self.http_client.ws_connect(uri, params=params)
        else:
            return self.http_client.request(
                method, uri, params=params)


class Resource(object):
    """Swagger resource, described in an API declaration.

    :param resource: Resource model
    :param http_client: HTTP client API
    """

    def __init__(self, resource, http_client, basePath):
        log.debug(u"Building resource '%s'" % resource[u'name'])
        log.debug( "*** %s %s " , resource, basePath )
        self.__json = resource
        decl = resource['api_declaration']
        self.__http_client = http_client
        self.__basePath = basePath
        self.__operations = dict(
                (oper['nickname'], self._build_operation(decl, api, oper))
            for api in decl['apis']
            for oper in api['operations'])
        for key in self.__operations:
            setattr(self, key, self.__get_operation(key))

    def __repr__(self):
        return u"%s(%s)" % (self.__class__.__name__, self.__json[u'name'])

    def __getattr__(self, item):
        """Promote operations to be object fields.

        :param item: Name of the attribute to get.
        :rtype: Resource
        :return: Resource object.
        """
        op = self.__get_operation(item)
        if not op:
            raise AttributeError(u"Resource '%s' has no operation '%s'" %
                                 (self.__get_name(), item))
        return op

    def __get_operation(self, name):
        """Gets the operation with the given nickname.

        :param name: Nickname of the operation.
        :rtype:  Operation
        :return: Operation, or None if not found.
        """
        return self.__operations.get(name)

    def __get_name(self):
        """Returns the name of this resource.

        Name is derived from the filename of the API declaration.

        :return: Resource name.
        """
        return self.__json.get(u'name')

    def _build_operation(self, decl, api, operation):
        """Build an operation object

        :param decl: API declaration.
        :param api: API entry.
        :param operation: Operation.
        """
        log.debug(u"Building operation %s.%s" % (
            self.__get_name(), operation[u'nickname']))
        log.debug(" ++++ %s %s %s", decl, api, operation)
        basePath = self.__basePath if decl[u'basePath'] == '/' else decl[u'basePath']
        uri = basePath + api[u'path']
        return Operation(uri, operation, self.__http_client)


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
        self.__http_client = http_client

        loader = swaggerpy.Loader(
            http_client, [WebsocketProcessor(), ClientProcessor()])

        if isinstance(url_or_resource, unicode):
            log.debug(u"Loading from %s" % url_or_resource)
            self.__api_docs = loader.load_resource_listing(url_or_resource)
            parsed_uri = urlparse(url_or_resource)
            basePath = '{uri.scheme}://{uri.netloc}'.format(uri=parsed_uri)
        else:
            log.debug(u"Loading from %s" % url_or_resource.get(u'basePath'))
            self.__api_docs = url_or_resource
            loader.process_resource_listing(self.__api_docs)
            basePath = url_or_resource.get(u'basePath')
        
        self.__resources = {}
        for resource in self.__api_docs[u'apis']:
            self.__resources[resource[u'name']] = Resource(resource, http_client, basePath)
            setattr(self, resource["name"], self.__get_resource(resource[u'name']))

    def __repr__(self):
        return u"%s(%s)" % (self.__class__.__name__, self.__api_docs.get(u'basePath'))

    def __getattr__(self, item):
        """Promote resource objects to be client fields.

        :param item: Name of the attribute to get.
        :return: Resource object.
        """
        resource = self.__get_resource(item)
        if not resource:
            raise AttributeError(u"API has no resource '%s'" % item)
        return resource

    def close(self):
        """Close the SwaggerClient, and underlying resources.
        """
        self.__http_client.close()

    def __get_resource(self, name):
        """Gets a Swagger resource by name.

        :param name: Name of the resource to get
        :rtype: Resource
        :return: Resource, or None if not found.
        """
        return self.__resources.get(name)
