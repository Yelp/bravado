#
# Copyright (c) 2013, Digium, Inc.
# Copyright (c) 2014, Yelp, Inc.
#

"""Swagger client library.
"""

import json
import logging
import os.path
import time
import urllib
from collections import namedtuple
from urlparse import urlparse

import swagger_type
from swaggerpy.http_client import APP_FORM, APP_JSON, SynchronousHttpClient
from swaggerpy.processors import WebsocketProcessor, SwaggerProcessor
from swaggerpy.response import HTTPFuture, SwaggerResponse
from swaggerpy.swagger_model import create_model_type, Loader
from swaggerpy.swagger_type import SwaggerTypeCheck

log = logging.getLogger(__name__)

SWAGGER_SPEC_TIMEOUT_S = 300


class CachedClient(object):
    """A wrapper to client which stores the last updated timestamp and the
    timeout in secs. when the client expires

    :param swagger_client: Core SwaggerClient instance
    :type swagger_client: :class:`SwaggerClient`
    :param timeout: timeout in seconds after which the client expires
    :type timeout: int
    """

    def __init__(self, swagger_client, timeout, timestamp=None):
        self.swagger_client = swagger_client
        self.timeout = timeout
        self.timestamp = timestamp or time.time()

    def is_stale(self, timestamp=None):
        """Checks if the instance has become stale
        :return: true/false whether client is now stale
        """
        current_time = timestamp or time.time()
        return self.timestamp + self.timeout < current_time


class SwaggerClientFactory(object):
    """Factory to store swagger clients and refetch the api-docs if the client
    becomes stale
    """

    def __init__(self):
        self.cache = dict()

    def __call__(self, api_docs_url, *args, **kwargs):
        """
        :param api_docs_url: url for swagger api docs used to build the client
        :type api_docs_url: str
        :param timeout: (optional) Timeout after which api-docs is stale
        :return: :class:`CachedClient`
        """
        # Construct cache key out of api_docs_url
        if isinstance(api_docs_url, (str, unicode)):
            key = api_docs_url
        else:
            key = json.dumps(api_docs_url)

        if (key not in self.cache or
                self.cache[key].is_stale()):
            self.cache[key] = self.build_cached_client(api_docs_url, *args,
                                                       **kwargs)
        return self.cache[key]

    def build_cached_client(self, *args, **kwargs):
        """Builds a fresh SwaggerClient and stores it in a namedtuple which
        contains its created timestamp and timeout in seconds
        """
        timeout = kwargs.pop('timeout', SWAGGER_SPEC_TIMEOUT_S)
        return CachedClient(SwaggerClient(*args, **kwargs), timeout)

factory = None


def get_client(*args, **kwargs):
    """Factory method to generate SwaggerClient instance.

    .. note::

        This factory method uses a global which maintains the state of swagger
        client. Use :class:`SwaggerClientFactory` if you want more control.

    To change the freshness timeout, simply pass an argument: timeout=<sec.>

    To remove the caching functionality, pass: timeout=0

    .. note::

       It is OKAY to call get_swagger_client(...) again and again.
       Do not assign a reference to the generated client and make it long
       lived as it strips out the refetching functionality.

    :param api_docs_url: url for swagger api docs used to build the client
    :type api_docs_url: str
    :param timeout: (optional) Timeout in secs. after which api-docs is stale
    :return: :class:`SwaggerClient`
    """
    global factory

    if factory is None:
        factory = SwaggerClientFactory()

    return factory(*args, **kwargs).swagger_client


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
        self._uri = uri
        self._json = operation
        self._http_client = http_client
        self._models = models
        self.__doc__ = create_operation_docstring(operation)

    def __repr__(self):
        return u"%s(%s)" % (self.__class__.__name__, self._json[u'nickname'])

    def _construct_request(self, **kwargs):
        request = {}
        request['method'] = self._json[u'method']
        request['url'] = self._uri
        request['params'] = {}
        # Copy the client's headers so that other headers could
        # be added during this construction w/o changing the former
        request['headers'] = self._http_client._headers.copy()
        for param in self._json.get(u'parameters', []):
            value = kwargs.pop(param[u'name'], default_value(param))
            validate_and_add_params_to_request(param, value, request,
                                               self._models)
        if kwargs:
            raise TypeError(u"'%s' does not have parameters %r" % (
                self._json[u'nickname'], kwargs.keys()))
        return request

    def __call__(self, **kwargs):
        log.info(u"%s?%r" % (self._json[u'nickname'],
                             urllib.urlencode(kwargs)))
        if self._json[u'is_websocket']:
            raise AssertionError("Websockets aren't supported in this version")
        request = self._construct_request(**kwargs)

        def py_model_convert_callback(response, **kwargs):
            value = None
            type_ = swagger_type.get_swagger_type(self._json)
            # Assume status is OK,
            # as exception would have been raised otherwise
            # Validate the response if it is not empty.
            if response.text:
                # Validate and convert API response to Python model instance
                value = SwaggerResponse(
                    response.json(), type_, self._models,
                    **kwargs).swagger_object
            return value
        return HTTPFuture(self._http_client,
                          request, py_model_convert_callback)


class Resource(object):
    """Swagger resource, described in an API declaration.

    :param resource: Resource model
    :param http_client: HTTP client API
    :param basePath: url path used for api-docs fetch
    """

    def __init__(self, resource, http_client, base_path):
        log.debug(u"Building resource '%s'" % resource[u'name'])
        self._json = resource
        decl = resource['api_declaration']
        self._http_client = http_client
        self._base_path = base_path
        self._set_models()
        self._operations = dict(
            (oper['nickname'], self._build_operation(decl, api, oper))
            for api in decl['apis']
            for oper in api['operations'])
        for key in self._operations:
            setattr(self, key, self._get_operation(key))

    def _set_models(self):
        """Create namedtuple of model types created from 'api_declaration'
        """
        models_dict = self._json['api_declaration'].get('models', {})
        models = namedtuple('models', models_dict.keys())
        keys_to_models = {}
        for key in models_dict.keys():
            keys_to_models[key] = create_model_type(models_dict[key])
        self.models = models(**keys_to_models)

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
        # IF basePath starts with /, prepend it with stored host name
        if decl[u'basePath'].startswith('/'):
            if urlparse(self._base_path).scheme == 'file':
                raise AssertionError(
                    "Base path can't start with / for local specs," +
                    " unless api_base_path is passed to SwaggerClient.")
            base_path = self._base_path.strip('/') + decl['basePath']
        else:
            base_path = decl[u'basePath']
        uri = base_path.strip('/') + api[u'path']
        return Operation(uri, operation, self._http_client, self.models)


class SwaggerClient(object):
    """Client object for accessing a Swagger-documented RESTful service.

    :param url_or_resource: Either the parsed resource listing+API decls, or
                            its URL.
    :type url_or_resource: dict or str
    :param http_client: HTTP client API
    :type  http_client: HttpClient
    :param api_base_path: Base Path for making API calls
    :type api_base_path: str
    :param raise_with: Custom Exception to wrap the response error with
    :type raise_with: type
    """

    def __init__(self, url_or_resource, http_client=None,
                 api_base_path=None, raise_with=None):
        if not http_client:
            http_client = SynchronousHttpClient()
        # Wrap http client's errors with raise_with
        http_client.raise_with = raise_with
        self._http_client = http_client

        # Load Swagger APIs always synchronously
        loader = Loader(
            SynchronousHttpClient(headers=http_client._headers),
            [WebsocketProcessor(), ClientProcessor()])

        forced_api_base_path = api_base_path is not None
        # url_or_resource can be url of type str,
        # OR a dict of resource itself.
        if isinstance(url_or_resource, (str, unicode)):
            log.debug(u"Loading from %s" % url_or_resource)
            self._api_docs = loader.load_resource_listing(url_or_resource)
            parsed_uri = urlparse(url_or_resource)
            if not api_base_path:
                api_base_path = "{uri.scheme}://{uri.netloc}".format(
                    uri=parsed_uri)
        else:
            log.debug(u"Loading from %s" % url_or_resource.get(u'url'))
            self._api_docs = url_or_resource
            loader.process_resource_listing(self._api_docs)
            if not api_base_path:
                api_base_path = url_or_resource.get(u'url')

        self._resources = {}
        for resource in self._api_docs[u'apis']:
            if forced_api_base_path and 'api_declaration' in resource:
                resource['api_declaration']['basePath'] = api_base_path
            self._resources[resource[u'name']] = Resource(
                resource, http_client, api_base_path)
            setattr(self, resource['name'],
                    self._get_resource(resource[u'name']))

    def __repr__(self):
        return u"%s(%s)" % (self.__class__.__name__,
                            self._api_docs.get(u'url'))

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


def _build_param_string(param):
    """Builds param docstring from the param dict

    :param param: data to create docstring from
    :type param: dict
    :returns: string giving meta info

    Example: ::
        status (string) : Statuses to be considered for filter
        from_date (string) : Start date filter"
    """
    string = "\t" + param.get("name")
    type_ = param.get('$ref') or param.get('format') or param.get('type')
    if type_:
        string += (" (%s) " % type_)
    if param.get('description'):
        string += ": " + param["description"]
    return string + "\n"


def create_operation_docstring(json_):
    """Builds Operation docstring from the json dict

    :param json_: data to create docstring from
    :type json_: dict
    :returns: string giving meta info

    Example: ::

        client.pet.findPetsByStatus?

    Outputs: ::

        [GET] Finds Pets by status

        Multiple status values can be provided with comma seperated strings
        Args:
                status (string) : Statuses to be considered for filter
                from_date (string) : Start date filter
        Returns:
                array
        Raises:
                400: Invalid status value
    """
    docstring = ""
    if json_.get('summary'):
        docstring += ("[%s] %s\n\n" % (json_['method'], json_.get('summary')))
    docstring += (json_["notes"] + "\n") if json_.get("notes") else ''

    if json_["parameters"]:
        docstring += "Args:\n"
        for param in json_["parameters"]:
            docstring += _build_param_string(param)
    if json_.get('type'):
        docstring += "Returns:\n\t%s\n" % json_["type"]
    if json_.get('responseMessages'):
        docstring += "Raises:\n"
        for msg in json_.get('responseMessages'):
            docstring += "\t%s: %s\n" % (msg.get("code"), msg.get("message"))
    return docstring


def handle_form_param(name, value, type_, request):
    request['headers']['content-type'] = APP_FORM
    if swagger_type.is_file(type_):
        if 'files' not in request:
            request['files'] = {}
        request['files'][name] = value
    elif swagger_type.is_primitive(type_):
        if 'data' not in request:
            request['data'] = {}
        request['data'][name] = value
    else:
        raise AssertionError(
            u"%s neither primitive nor File" % name)


def add_param_to_req(param, value, request):
    """Populates request object with the request parameters

    :param param: swagger spec details of a param
    :type param: dict
    :param value: value for the param given in the API call
    :param request: request object to be populated
    """
    pname = param['name']
    type_ = swagger_type.get_swagger_type(param)
    param_req_type = param['paramType']

    if param_req_type == u'path':
        request['url'] = request['url'].replace(
            u'{%s}' % pname, unicode(value))
    elif param_req_type == u'query':
        request['params'][pname] = value
    elif param_req_type == u'body':
        request['data'] = value
        if not swagger_type.is_primitive(type_):
            # If not primitive, body has to be 'dict'
            # (or has already been converted to dict from model)
            request['headers']['content-type'] = APP_JSON
    elif param_req_type == 'form':
        handle_form_param(pname, value, type_, request)
    # TODO(#31): accept 'header', in paramType
    else:
        raise AssertionError(
            u"Unsupported Parameter type: %s" % param_req_type)


def default_value(param):
    """Fetches if present for param, returns None otherwise
    Validation of the type happens later.
    """
    return param.get('defaultValue')


def validate_and_add_params_to_request(param, value, request, models):
    """Validates if a required param is given
    And wraps 'add_param_to_req' to populate a valid request

    :param param: swagger spec details of a param
    :type param: dict
    :param value: value for the param given in the API call
    :param request: request object to be populated
    :param models: models tuple containing all complex model types
    :type models: namedtuple
    """
    # If param not given in args, and not required, just ignore.
    if not param.get('required') and not value:
        return

    pname = param['name']
    type_ = swagger_type.get_swagger_type(param)
    param_req_type = param['paramType']

    if param_req_type == 'path':
        # Parameters in path need to be primitive/array types
        if swagger_type.is_complex(type_):
            raise TypeError("Param %s in path can only be primitive/list" %
                            pname)
    elif param_req_type == 'query':
        # Parameters in query need to be only primitive types
        if not swagger_type.is_primitive(type_):
            raise TypeError("Param %s in query can only be primitive" % pname)

    # Allow lists for query params even if type is primitive
    if isinstance(value, list) and param_req_type == 'query':
        type_ = swagger_type.ARRAY + swagger_type.COLON + type_

    # Check the parameter value against its type
    # And store the refined value back
    value = SwaggerTypeCheck(pname, value, type_, models).value

    # If list in path, Turn list items into comma separated values
    if isinstance(value, list) and param_req_type == 'path':
        value = u",".join(str(x) for x in value)

    # Add the parameter value to the request object
    if value is not None:
        add_param_to_req(param, value, request)
    else:
        if param.get(u'required'):
            raise TypeError(u"Missing required parameter '%s'" % pname)
