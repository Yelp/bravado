# -*- coding: utf-8 -*-
"""
The :class:`SwaggerClient` provides an interface for making API calls based on
a swagger spec, and returns responses of python objects which build from the
API response.


Structure Diagram::

        +---------------------+           +---------------------+
        |                     |           |                     |
        |    SwaggerClient    <-----------+  SwaggerClientCache |
        |                     |   caches  |                     |
        +------+--------------+           +---------------------+
               |
               |  has many
               |
        +------v--------------+
        |                     |
        |     Resource        +------------------+
        |                     |                  |
        +------+--------------+         has many |
               |                                 |
               |  has many                       |
               |                                 |
        +------v--------------+           +------v--------------+
        |                     |           |                     |
        |     Operation       |           |    SwaggerModel     |
        |                     |           |                     |
        +------+--------------+           +---------------------+
               |
               |  uses
               |
        +------v--------------+
        |                     |
        |     HttpClient      |
        |                     |
        +---------------------+


To get a client with caching

.. code-block:: python

        client = swaggerpy.client.get_client(api_docs_url)

without caching

.. code-block:: python

        client = swaggerpy.client.SwaggerClient.from_url(api_docs_url)

"""

from swaggerpy.compat import json
import logging
import os.path
import time
import urllib
from urlparse import urlparse

from yelp_uri import urllib_utf8

import swagger_type
from swaggerpy.http_client import APP_JSON, SynchronousHttpClient
from swaggerpy.response import HTTPFuture, post_receive
from swaggerpy.swagger_model import (
    create_model_type,
    is_file_scheme_uri,
    load_resource_listing,
)
from swaggerpy.swagger_type import SwaggerTypeCheck

log = logging.getLogger(__name__)

SWAGGER_SPEC_CACHE_TTL = 300


class CacheEntry(object):
    """An entry in the cache. Each item has it's own ttl.

    :param item: the item to cache
    :param ttl: time-to-live in seconds after which the client expires
    :type  ttl: int
    """

    def __init__(self, item, ttl, timestamp=None):
        self.item = item
        self.ttl = ttl
        self.timestamp = timestamp or time.time()

    def is_stale(self, timestamp=None):
        """Checks if the instance has become stale
        :return: True if the cache item is stale, False otherwise
        """
        current_time = timestamp or time.time()
        return self.timestamp + self.ttl < current_time


class SwaggerClientCache(object):
    """Cache to store swagger clients and refetch the api-docs if the client
    becomes stale
    """

    def __init__(self):
        self.cache = dict()

    def __contains__(self, key):
        return key in self.cache and not self.cache[key].is_stale()

    def __call__(self, *args, **kwargs):
        # timeout is backwards compatible with 0.7
        ttl = kwargs.pop('ttl', kwargs.pop('timeout', SWAGGER_SPEC_CACHE_TTL))
        key = repr(args) + repr(sorted(kwargs.iteritems()))

        if key not in self:
            self.cache[key] = CacheEntry(
                self.build_client(*args, **kwargs), ttl)

        return self.cache[key].item

    def build_client(self, api_docs, *args, **kwargs):
        if isinstance(api_docs, basestring):
            return SwaggerClient.from_url(api_docs, *args, **kwargs)
        return SwaggerClient.from_resource_listing(api_docs, *args, **kwargs)


cache = None


def get_client(*args, **kwargs):
    """Factory method to generate SwaggerClient instance.

    .. note::

        This factory method uses a global which maintains the state of swagger
        client. Use :class:`SwaggerClientCache` if you want more control.

    To change the freshness timeout, simply pass an argument: ttl=<seconds>

    To remove the caching functionality, pass: ttl=0

    .. note::

       It is OKAY to call get_swagger_client(...) again and again.
       Do not keep a reference to the generated client and make it long
       lived as it strips out the refetching functionality.

    :param api_docs_url: url for swagger api docs used to build the client
    :type  api_docs_url: str
    :param ttl: (optional) Timeout in secs. after which api-docs is stale
    :return: :class:`SwaggerClient`
    """
    global cache

    if cache is None:
        cache = SwaggerClientCache()

    return cache(*args, **kwargs)


class Operation(object):
    """Perform a request by taking the kwargs passed to the call and
    constructing an HTTP request.
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
        _request_options = kwargs.pop('_request_options', {}) or {}

        request = {}
        # The requests library expects native strings. Without this, POST
        # with a binary file upload throws a UnicodeDecodeError.
        request['method'] = str(self._json[u'method'])
        request['url'] = self._uri
        request['params'] = {}
        request['headers'] = _request_options.get('headers', {}) or {}

        for param in self._json.get(u'parameters', []):
            value = kwargs.pop(param[u'name'], param.get('defaultValue'))
            validate_and_add_params_to_request(param, value, request,
                                               self._models)
        if kwargs:
            raise TypeError(u"'%s' does not have parameters %r" % (
                self._json[u'nickname'], kwargs.keys()))
        return request

    def __call__(self, **kwargs):
        log.debug(u"%s?%r" % (
            self._json[u'nickname'],
            urllib_utf8.urlencode(kwargs)))
        request = self._construct_request(**kwargs)

        def response_future(response, **kwargs):
            # Assume status is OK, an exception would have been raised already
            if not response.text:
                return None

            return post_receive(
                response.json(),
                swagger_type.get_swagger_type(self._json),
                self._models,
                **kwargs)
        return HTTPFuture(self._http_client, request, response_future)


def build_models(model_dicts):
    return dict(
        (name, create_model_type(model_def))
        for name, model_def in model_dicts.iteritems())


def get_resource_url(base_path, url_base, resource_base_path):
    if base_path:
        return base_path

    if url_base and resource_base_path.startswith('/'):
        if is_file_scheme_uri(url_base):
            raise AssertionError("Can't resolve relative resource urls with a "
                                 " file:// url, for %s." % resource_base_path)
        return url_base.rstrip('/') + resource_base_path

    return resource_base_path


class Resource(object):
    """Swagger resource, described in an API declaration.
    """

    def __init__(self, name, operations):
        log.debug(u"Building resource '%s'" % name)
        self._name = name
        self._operations = operations

    @classmethod
    def from_api_doc(cls, api_doc, http_client, base_path, url_base=None):
        """
        :param api_doc: api doc which defines this resource
        :type  api_doc: :class:`dict`
        :param http_client: a :class:`swaggerpy.http_client.HttpClient`
        :param base_path: base url to perform api requests. Used to override
                the path provided in the api spec
        :param url_base: a url used as the base for resource definitions
                that include a relative basePath
        """
        declaration = api_doc['api_declaration']
        models = build_models(declaration.get('models', {}))

        def build_operation(api_obj, operation):
            log.debug(u"Building operation %s.%s" % (
                api_obj.get('name'), operation['nickname']))

            resource_base_path = declaration.get('basePath')
            url = get_resource_url(base_path, url_base, resource_base_path)
            url = url.rstrip('/') + api_obj['path']
            return Operation(url, operation, http_client, models)

        operations = dict(
            (oper['nickname'], build_operation(api, oper))
            for api in declaration['apis']
            for oper in api['operations'])
        return cls(api_doc['name'], operations)

    def __repr__(self):
        return u"%s(%s)" % (self.__class__.__name__, self._name)

    def __getattr__(self, item):
        """
        :param item: name of the :class:`Operation` to return
        :return: an :class:`Operation`
        """
        op = self._operations.get(item)
        if not op:
            raise AttributeError(u"Resource '%s' has no operation '%s'" %
                                 (self._name, item))
        return op

    def __dir__(self):
        return self._operations.keys()


class SwaggerClient(object):
    """A client for accessing a Swagger-documented RESTful service.

    :param api_url: the url for the swagger api docs, only used for the repr.
    :param resources: a list of :Resource: objects used to perform requests
    """

    def __init__(self, api_url, resources):
        self._api_url = api_url
        self._resources = resources

    @classmethod
    def from_url(
            cls,
            url,
            http_client=None,
            api_base_path=None,
            request_options=None):
        """
        Build a :class:`SwaggerClient` from a url to api docs describing the
        api.

        :param url: url pointing at the swagger api docs
        :type url: str
        :param http_client: an HTTP client used to perform requests
        :type  http_client: :class:`swaggerpy.http_client.HttpClient`
        :param api_base_path: a url, override the path used to make api requests
        :type  api_base_path: str
        :param request_options: extra values to pass with api docs requests
        :type  request_options: dict
        """
        log.debug(u"Loading from %s" % url)
        http_client = http_client or SynchronousHttpClient()

        return cls.from_resource_listing(
            load_resource_listing(url, http_client, None, request_options),
            http_client=http_client,
            api_base_path=api_base_path,
            url=url)

    @classmethod
    def from_resource_listing(
            cls,
            resource_listing,
            http_client=None,
            api_base_path=None,
            url=None):
        """
        Build a :class:`SwaggerClient` from swagger api docs

        :param resource_listing: a dict with a list of api definitions
        :param http_client: an HTTP client used to perform requests
        :type  http_client: :class:`swaggerpy.http_client.HttpClient`
        :param api_base_path: a url, override the path used to make api requests
        :type  api_base_path: str
        :param url: the url used to retrieve the resource listing
        :type  url: str
        """
        url = url or resource_listing.get(u'url')
        log.debug(u"Using resources from %s" % url)

        if url:
            url_base = "{uri.scheme}://{uri.netloc}".format(uri=urlparse(url))
        else:
            url_base = None

        resources = build_resources_from_spec(
            http_client or SynchronousHttpClient(),
            map(append_name_to_api, resource_listing['apis']),
            api_base_path,
            url_base)
        return cls(url, resources)

    def __repr__(self):
        return u"%s(%s)" % (self.__class__.__name__, self._api_url)

    def __getattr__(self, item):
        """
        :param item: name of the resource to return
        :return: :class:`Resource`
        """
        resource = self._resources.get(item)
        if not resource:
            raise AttributeError(u"API has no resource '%s'" % item)
        return resource

    def __dir__(self):
        return self._resources.keys()


def build_resources_from_spec(http_client, apis, api_base_path, url_base):
    return dict(
        (api_doc['name'],
         Resource.from_api_doc(api_doc, http_client, api_base_path, url_base))
        for api_doc in apis)


def append_name_to_api(api_entry):
    name, ext = os.path.splitext(os.path.basename(api_entry['path']))
    return dict(api_entry, name=name)


def _build_param_docstring(param):
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
            docstring += _build_param_docstring(param)
    if json_.get('type'):
        docstring += "Returns:\n\t%s\n" % json_["type"]
    if json_.get('responseMessages'):
        docstring += "Raises:\n"
        for msg in json_.get('responseMessages'):
            docstring += "\t%s: %s\n" % (msg.get("code"), msg.get("message"))
    return docstring


def handle_form_param(name, value, type_, request):
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
            u'{%s}' % pname,
            urllib.quote(unicode(value)))
    elif param_req_type == u'query':
        request['params'][pname] = value
    elif param_req_type == u'body':
        if not swagger_type.is_primitive(type_):
            # If not primitive, body has to be 'dict'
            # (or has already been converted to dict from model)
            request['headers']['content-type'] = APP_JSON
            request['data'] = json.dumps(value)
        else:
            request['data'] = stringify_body(value)
    elif param_req_type == 'form':
        handle_form_param(pname, value, type_, request)
    elif param_req_type == 'header':
        if pname in request['headers']:
            log.warn(u'Header {0}:{1} has been overridden by {0}:{2}'.format(
                pname, value, request['headers'][pname]))
        else:
            request['headers'][pname] = value
    else:
        raise AssertionError(
            u"Unsupported Parameter type: %s" % param_req_type)


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
    if not param.get('required') and value is None:
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

    # TODO: this needs to move to add_param_to_req, and change logic
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


def stringify_body(value):
    """Json dump the value to string if not already in string
    """
    if not value or isinstance(value, basestring):
        return value
    return json.dumps(value)
