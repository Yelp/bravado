# -*- coding: utf-8 -*-
"""
The :class:`SwaggerClient` provides an interface for making API calls based on
a swagger spec, and returns responses of python objects which build from the
API response.

Structure Diagram::

        +---------------------+
        |                     |
        |    SwaggerClient    |
        |                     |
        +------+--------------+
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


To get a client

.. code-block:: python

        client = bravado.client.SwaggerClient.from_url(swagger_spec_url)
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


class SwaggerClient(object):
    """A client for accessing a Swagger-documented RESTful service.
    """

    def __init__(self, swagger_spec):
        """
        :param swagger_spec: :class:`bravado.mapping.spec.Spec`
        """
        self.swagger_spec = swagger_spec

    @classmethod
    def from_url(cls, spec_url, http_client=None, request_headers=None):
        """
        Build a :class:`SwaggerClient` from a url to the Swagger
        specification for a RESTful API.

        :param spec_url: url pointing at the swagger API specification
        :type spec_url: str
        :param http_client: an HTTP client used to perform requests
        :type  http_client: :class:`bravado.http_client.HttpClient`
        :param request_headers: Headers to pass with http requests
        :type  request_headers: dict
        """
        # TODO: better way to customize the request for api calls, so we don't
        #       have to add new kwargs for everything
        log.debug(u"Loading from %s" % spec_url)
        http_client = http_client or SynchronousHttpClient()
        loader = Loader(http_client, request_headers=request_headers)
        spec_dict = loader.load_spec(spec_url)
        return cls.from_spec(spec_dict, spec_url, http_client)

    @classmethod
    def from_spec(cls, spec_dict, origin_url=None, http_client=None):
        """
        Build a :class:`SwaggerClient` from swagger api docs

        :param spec_dict: a dict with a Swagger spec in json-like form
        :param origin_url: the url used to retrieve the spec_dict
        :type  origin_url: str
        """
        swagger_spec = Spec.from_dict(spec_dict, origin_url, http_client)
        return cls(swagger_spec)

    def get_model(self, model_name):
        return self.swagger_spec.definitions[model_name]

    def __repr__(self):
        return u"%s(%s)" % (self.__class__.__name__, self.swagger_spec.api_url)

    def __getattr__(self, item):
        """
        :param item: name of the resource to return
        :return: :class:`Resource`
        """
        resource = self.swagger_spec.resources.get(item)
        if not resource:
            raise AttributeError(u"API has no resource '%s'" % item)
        return resource

    def __dir__(self):
        return self.swagger_spec.resources.keys()
