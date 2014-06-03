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
from collections import namedtuple

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
        name, ext = os.path.splitext(os.path.basename(listing_api[u'path']))
        listing_api[u'name'] = name


class Operation(object):
    """Operation object.
    """

    def __init__(self, uri, operation, http_client, models):
        self.uri = uri
        self.json = operation
        self.http_client = http_client
        self.models = models

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
        data = None; headers = None
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
                elif param[u'paramType'] == u'body':
                    data = value; headers = {'content-type':'application/json'}
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
            response = self.http_client.ws_connect(uri, params=params)
        else:
            response = self.http_client.request(method, uri, params, data, headers)
        type = self.json.get(u'type')
        if is_complex_type(type):
            setattr(response, 'model', getattr(self.models, type)())
            #ToDo: populate response.model
        else:
            setattr(response, 'model', None)
        return response

def is_complex_type(type):
    primitive_types = [u'void', u'int32', u'int64', u'float',
            u'double', u'byte', u'date', u'date-time']
    non_complex_types = primitive_types + ['array']
    if type not in non_complex_types:
        return type

def get_types(props):
    swagger_types = {}
    for prop in props.keys():
        _type = props[prop].get('type')
        _format = props[prop].get('format') 
        _ref = props[prop].get('$ref')
        _item = props[prop].get('items')
        if _item:
            _item_type = _item.get('$ref') or \
            _item.get('format') or \
            _item.get('type')
        if _format:
            swagger_types[prop] = _format
        elif _type == "array":
            swagger_types[prop] = _type+"["+_item_type+"]"
        elif _ref:
            swagger_types[prop] = _ref
        elif _type:
            swagger_types[prop] = _type
    return swagger_types


class Resource(object):
    """Swagger resource, described in an API declaration.

    :param resource: Resource model
    :param http_client: HTTP client API
    """

    def __init__(self, resource, http_client, basePath):
        log.debug(u"Building resource '%s'" % resource[u'name'])
        self._json = resource
        decl = resource['api_declaration']
        self._http_client = http_client
        self._basePath = basePath
        self._set_models()
        self._operations = dict(
                (oper['nickname'], self._build_operation(decl, api, oper))
            for api in decl['apis']
            for oper in api['operations'])
        for key in self._operations:
            setattr(self, key, self._get_operation(key))

    def _set_models(self):
        models_dict = self._json['api_declaration']['models']
        models = namedtuple('models', models_dict.keys())
        keys = {}
        for key in models_dict.keys():
            props = models_dict[key]['properties']
            def set_props(this, props):
                for prop in props.keys():
                    setattr(this, prop, None)

            keys[key] = type(str(key), (object,), dict(__init__ = lambda self: set_props(self, props)))
            setattr(keys[key], 'swagger_types', get_types(props))
            setattr(keys[key], 'required', models_dict[key].get('required'))
        self.models = models(**keys)
        
    def __repr__(self):
        return u"%s(%s)" % (self.__class__.__name__, self._json[u'name'])

    def __getattr__(self, item):
        """Promote operations to be object fields.

        :param item: Name of the attribute to get.
        :rtype: Resource
        :return: Resource object.
        """
        op = self._get_operation(item)
        if not op:
            raise AttributeError(u"Resource '%s' has no operation '%s'" %
                                 (self._get_name(), item))
        return op

    def _get_operation(self, name):
        """Gets the operation with the given nickname.

        :param name: Nickname of the operation.
        :rtype:  Operation
        :return: Operation, or None if not found.
        """
        return self._operations.get(name)

    def _get_name(self):
        """Returns the name of this resource.

        Name is derived from the filename of the API declaration.

        :return: Resource name.
        """
        return self._json.get(u'name')

    def _build_operation(self, decl, api, operation):
        """Build an operation object

        :param decl: API declaration.
        :param api: API entry.
        :param operation: Operation.
        """
        log.debug(u"Building operation %s.%s" % (
            self._get_name(), operation[u'nickname']))
        basePath = self._basePath if decl[u'basePath'] == '/' else decl[u'basePath']
        uri = basePath + api[u'path']
        return Operation(uri, operation, self._http_client, self.models)


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
        self._http_client = http_client

        loader = swaggerpy.Loader(
            http_client, [WebsocketProcessor(), ClientProcessor()])

        if isinstance(url_or_resource, unicode):
            log.debug(u"Loading from %s" % url_or_resource)
            self._api_docs = loader.load_resource_listing(url_or_resource)
            parsed_uri = urlparse(url_or_resource)
            basePath = '{uri.scheme}://{uri.netloc}'.format(uri=parsed_uri)
        else:
            log.debug(u"Loading from %s" % url_or_resource.get(u'basePath'))
            self._api_docs = url_or_resource
            loader.process_resource_listing(self._api_docs)
            basePath = url_or_resource.get(u'basePath')

        self._resources = {}
        for resource in self._api_docs[u'apis']:
            self._resources[resource[u'name']] = Resource(resource, http_client, basePath)
            setattr(self, resource["name"], self._get_resource(resource[u'name']))

    def __repr__(self):
        return u"%s(%s)" % (self.__class__.__name__, self._api_docs.get(u'basePath'))

    def __getattr__(self, item):
        """Promote resource objects to be client fields.

        :param item: Name of the attribute to get.
        :return: Resource object.
        """
        resource = self._get_resource(item)
        if not resource:
            raise AttributeError(u"API has no resource '%s'" % item)
        return resource

    def close(self):
        """Close the SwaggerClient, and underlying resources.
        """
        self._http_client.close()

    def _get_resource(self, name):
        """Gets a Swagger resource by name.

        :param name: Name of the resource to get
        :rtype: Resource
        :return: Resource, or None if not found.
        """
        return self._resources.get(name)
