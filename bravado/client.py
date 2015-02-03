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

from bravado.http_client import SynchronousHttpClient
from bravado.swagger_model import (
    Loader,
    is_file_scheme_uri,
)
from bravado.mapping.spec import Spec

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
        loader = Loader(http_client, request_headers=request_headers)
        spec_dict = loader.load_spec(url)
        return cls.from_spec(spec_dict, origin_url=url, http_client=http_client)

    @classmethod
    def from_spec(cls, spec_dict, origin_url=None, http_client=None):
        """
        Build a :class:`SwaggerClient` from swagger api docs

        :param spec_dict: a dict with a Swagger spec in json-like form
        :param origin_url: the url used to retrieve the spec_dict
        :type  origin_url: str
        """
        spec = Spec.from_dict(spec_dict, origin_url, http_client)
        return cls(spec.api_url, spec.resources)

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












