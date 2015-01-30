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

        client = bravado.client.get_client(api_docs_url)

without caching

.. code-block:: python

        client = bravado.client.SwaggerClient.from_url(api_docs_url)

"""

import logging
import time
import urllib
import urlparse

from bravado.compat import json
from bravado.http_client import APP_JSON, SynchronousHttpClient
from bravado.mapping.model import build_models
from bravado.mapping.resource import build_resources
from bravado.swagger_model import (
    Loader,
    is_file_scheme_uri,
)
from bravado.swagger_type import SwaggerTypeCheck

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

    def build_client(self, spec_url_or_dict, *args, **kwargs):
        if isinstance(spec_url_or_dict, basestring):
            return SwaggerClient.from_url(spec_url_or_dict, *args, **kwargs)
        return SwaggerClient.from_spec(spec_url_or_dict, *args, **kwargs)


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


def get_resource_url(base_path, url_base, resource_base_path):
    if base_path:
        return base_path

    if url_base and resource_base_path.startswith('/'):
        if is_file_scheme_uri(url_base):
            raise AssertionError("Can't resolve relative resource urls with a "
                                 " file:// url, for %s." % resource_base_path)
        return url_base.rstrip('/') + resource_base_path

    return resource_base_path


class SwaggerClient(object):
    """A client for accessing a Swagger-documented RESTful service.

    :param api_url: the url for the swagger api docs, only used for the repr.
    :param resources: a dict of resource name to :Resource: objects used to
        perform requests.
    """

    def __init__(self, api_url, resources):
        self._api_url = api_url
        self._resources = resources

    @classmethod
    def from_url(
            cls,
            url,
            http_client=None,
            request_headers=None):
        """
        Build a :class:`SwaggerClient` from a url to api docs describing the
        api.

        :param url: url pointing at the swagger api docs
        :type url: str
        :param http_client: an HTTP client used to perform requests
        :type  http_client: :class:`bravado.http_client.HttpClient`
        :param request_headers: Headers to pass with api docs requests
        :type  request_headers: dict
        """
        log.debug(u"Loading from %s" % url)
        http_client = http_client or SynchronousHttpClient()

        # TODO: better way to customize the request for api-docs, so we don't
        # have to add new kwargs for everything
        loader = Loader(http_client, request_headers=request_headers)

        # Loads and validates the spec
        spec = loader.load_spec(url)

        return cls.from_spec(spec, http_client, origin_url=url)

    # @classmethod
    # def from_resource_listing(
    #         cls,
    #         resource_listing,
    #         http_client=None,
    #         api_base_path=None,
    #         url=None):
    #     """
    #     Build a :class:`SwaggerClient` from swagger api docs
    #
    #     :param resource_listing: a dict with a list of api definitions
    #     :param http_client: an HTTP client used to perform requests
    #     :type  http_client: :class:`bravado.http_client.HttpClient`
    #     :param api_base_path: a url, override the path used to make api
    #       requests
    #     :type  api_base_path: str
    #     :param api_doc_request_headers: Headers to pass with api docs requests
    #     :type  api_doc_request_headers: dict
    #     :param url: the url used to retrieve the resource listing
    #     :type  url: str
    #     """
    #     url = url or resource_listing.get(u'url')
    #     log.debug(u"Using resources from %s" % url)
    #
    #     if url:
    #         url_base = "{uri.scheme}://{uri.netloc}".format(uri=urlparse(url))
    #     else:
    #         url_base = None
    #
    #     resources = build_resources_from_spec(
    #         http_client or SynchronousHttpClient(),
    #         map(append_name_to_api, resource_listing['apis']),
    #         api_base_path,
    #         url_base)
    #     return cls(url, resources)

    @classmethod
    def from_spec(cls, spec, http_client=None, origin_url=None):
        """
        Build a :class:`SwaggerClient` from swagger api docs

        :param spec: a dict with a Swagger spec in json-like form
        :param http_client: an HTTP client used to perform requests
        :type  http_client: :class:`bravado.http_client.HttpClient`
        :param origin_url: the url used to retrieve the spec
        :type  origin_url: str
        """

        # Using 'x_' for the time being to identify things that
        # have been "tacked" onto the original spec dict
        spec['x_origin_url'] = origin_url
        spec['x_api_url'] = build_api_serving_url(spec, origin_url)
        http_client = http_client or SynchronousHttpClient()
        definitions = build_models(spec['definitions'])
        spec['x_definitions'] = definitions

        # START branch port_resource_and_ops
        resources = build_resources(spec, http_client)
        # END branch port_resource_and_ops

        return cls(spec['x_api_url'], resources)

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


def build_api_serving_url(spec, origin_url, preferred_scheme=None):
    """The URL used to service API requests does not necessarily have to be the
    same URL that was used to retrieve the API spec.

    The existence of three fields in the root of the specification govern
    the value of the api_serving_url:

    - host string
        The host (name or ip) serving the API. This MUST be the host only and
        does not include the scheme nor sub-paths. It MAY include a port.
        If the host is not included, the host serving the documentation is to
        be used (including the port). The host does not support path templating.

    - basePath string
        The base path on which the API is served, which is relative to the
        host. If it is not included, the API is served directly under the host.
        The value MUST start with a leading slash (/). The basePath does not
        support path templating.

    - schemes [string]
        The transfer protocol of the API. Values MUST be from the list:
        "http", "https", "ws", "wss". If the schemes is not included,
        the default scheme to be used is the one used to access the
        specification.

    See https://github.com/swagger-api/swagger-spec/blob/master/versions/2.0.md#swagger-object-   # noqa

    :param spec: the Swagger spec in json-like dict form
    :param origin_url: the URL from which the spec was retrieved
    :param preferred_scheme: preferred scheme to use if more than one scheme is
        supported by the API.
    :return: base url which services api requests
    """
    origin = urlparse.urlparse(origin_url)

    def pick_a_scheme(schemes):
        if not schemes:
            return origin.scheme

        if preferred_scheme:
            if preferred_scheme in schemes:
                return preferred_scheme
            raise Exception(
                "Preferred scheme {0} not supported by API. Available schemes "
                "include {1}".format(preferred_scheme, schemes))

        if origin.scheme in schemes:
            return origin.scheme

        if len(schemes) == 1:
            return schemes[0]

        raise Exception(
            "Origin scheme {0} not supported by API. Available schemes "
            "include {1}".format(origin.scheme, schemes))

    netloc = spec.get('host', origin.netloc)
    path = spec.get('basePath', origin.path)
    scheme = pick_a_scheme(spec.get('schemes'))

    return urlparse.urlunparse((scheme, netloc, path, None, None, None))


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
            # (or has already been converted to dict from model_dict)
            request['headers']['content-type'] = APP_JSON
            request['data'] = json.dumps(value)
        else:
            request['data'] = stringify_body(value)
    elif param_req_type == 'form':
        handle_form_param(pname, value, type_, request)
    # TODO(#31): accept 'header', in paramType
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
    :param models: models tuple containing all complex model_dict types
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
