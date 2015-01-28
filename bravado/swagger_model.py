# -*- coding: utf-8 -*-
import contextlib
from functools import partial
import logging
import os
import urllib
import urlparse

from swagger_spec_validator import validator20

from bravado import swagger_type
from bravado.compat import json
from bravado.http_client import SynchronousHttpClient
from mapping.model import create_model_repr, create_flat_dict
from mapping.docstring import docstring_property, create_model_docstring

log = logging.getLogger(__name__)


def is_file_scheme_uri(url):
    return urlparse.urlparse(url).scheme == u'file'


class FileEventual(object):
    """Adaptor which supports the :class:`crochet.EventualResult`
    interface for retrieving api docs from a local file.
    """

    class FileResponse(object):

        def __init__(self, data):
            self.data = data

        def json(self):
            return self.data

    def __init__(self, path):
        self.path = path

    def get_path(self):
        if not self.path.endswith('.json'):
            return self.path + '.json'
        return self.path

    def wait(self, timeout=None):
        with contextlib.closing(urllib.urlopen(self.get_path())) as fp:
            return self.FileResponse(json.load(fp))

    def cancel(self):
        pass


def start_request(http_client, url, headers):
    """Download and parse JSON from a URL.

    :param http_client: a :class:`bravado.http_client.HttpClient`
    :param url: url for api docs
    :return: an object with a :func`wait` method which returns the api docs
    """
    if is_file_scheme_uri(url):
        return FileEventual(url)

    request_params = {
        'method': 'GET',
        'url': url,
        'headers': headers,
    }
    return http_client.start_request(request_params)


class Loader(object):
    """Abstraction for loading Swagger API's.

    :param http_client: HTTP client interface.
    :type  http_client: http_client.HttpClient
    :param request_headers: dict of request headers
    """

    def __init__(self, http_client, request_headers=None):
        self.http_client = http_client
        self.request_headers = request_headers or {}

    def load_spec(self, spec_url, base_url=None):
        """Load a Swagger Spec from the given URL

        :param spec_url: URL to swagger.json
        :param base_url: TODO: need this?
        :returns: validated json spec in dict form
        """
        spec_json = start_request(
            self.http_client,
            spec_url,
            self.request_headers,
        ).wait().json()

        validator20.validate_spec(spec_json)
        return spec_json


# TODO: Adding the file scheme here just adds complexity to start_request()
# Is there a better way to handle this?
def load_file(spec_file, http_client=None):
    """Loads a spec file

    :param spec_file: Path to swagger.json.
    :param http_client: HTTP client interface.
    :return: validated json spec in dict form
    :raise: IOError: On error reading swagger.json.
    """
    file_path = os.path.abspath(spec_file)
    url = urlparse.urljoin(u'file:', urllib.pathname2url(file_path))
    # When loading from files, everything is relative to the spec file
    dir_path = os.path.dirname(file_path)
    base_url = urlparse.urljoin(u'file:', urllib.pathname2url(dir_path))
    return load_url(url, http_client=http_client, base_url=base_url)


def load_url(spec_url, http_client=None, base_url=None):
    """Loads a Swagger spec.

    :param spec_url: URL for swagger.json.
    :param http_client: HTTP client interface.
    :param base_url:    Optional URL to be the base URL for finding API
                        declarations. If not specified, 'basePath' from the
                        resource listing is used.
    :return: validated spec in dict form
    :raise: IOError, URLError: On error reading api-docs.
    """
    if http_client is None:
        http_client = SynchronousHttpClient()

    loader = Loader(http_client=http_client)
    return loader.load_spec(spec_url, base_url=base_url)


# AAA 1.2 - TODO purge w/ 1.2
# def create_model_type(model_dict):
#     """Create a dynamic class from the model_dict data defined in the swagger spec.
#
#     The docstring for this class is dynamically generated because generating
#     the docstring is relatively expensive, and would only be used in rare
#     cases for interactive debugging in a REPL.
#
#     :param model_dict: Resource model_dict :class:`dict` with keys `id` and `properties`
#     :returns: dynamic type created with attributes, docstrings attached
#     :rtype: type
#     """
#     props = model_dict['properties']
#     name = str(model_dict['id'])
#
#     methods = dict(
#         __doc__=docstring_property(partial(create_model_docstring, props)),
#         __eq__=lambda self, other: compare(self, other),
#         __init__=lambda self, **kwargs: set_props(self, **kwargs),
#         __repr__=lambda self: create_model_repr(self),
#         __dir__=lambda self: props.keys(),
#         _flat_dict=lambda self: create_flat_dict(self),
#         _swagger_types=swagger_type.get_swagger_types(props),
#         _required=model_dict.get('required'),
#     )
#     return type(name, (object,), methods)