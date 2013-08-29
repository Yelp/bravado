#
# Copyright (c) 2013, Digium, Inc.
#

import urllib
import urlparse
import os
import jsonify

from swagger_model import Loader


def load_file(resource_listing_file, processors=None, opener=None):
    """Loads a resource listing file, applying the given processors.

    @param resource_listing_file: File name for a resource listing.
    @param processors:  List of SwaggerProcessors to apply to the resulting
                        resource.
    @param opener:  Optional urllib2 opener for fetching API docs.
    @return: Processed object model from
    @raise IOError: On error reading api-docs.
    """
    file_path = os.path.abspath(resource_listing_file)
    url = urlparse.urljoin('file:', urllib.pathname2url(file_path))
    # When loading from files, everything is relative to the resource listing
    dir_path = os.path.dirname(file_path)
    base_url = urlparse.urljoin('file:', urllib.pathname2url(dir_path))
    return load_url(url, processors, opener=opener, base_url=base_url)


def load_url(resource_listing_url, processors=None, opener=None,
             base_url=None):
    """Loads a resource listing, applying the given processors.

    @param resource_listing_url: URL for a resource listing.
    @param processors:  List of SwaggerProcessors to apply to the resulting
                        resource.
    @param opener:  Optional urllib2 opener for fetching API docs.
    @param base_url:    Optional URL to be the base URL for finding API
                        declarations. If not specified, 'basePath' from the
                        resource listing is used.
    @return: Processed object model from
    @raise IOError, URLError: On error reading api-docs.
    """
    loader = Loader(processors)
    return loader.load_resource_listing(
        resource_listing_url, opener=opener, base_url=base_url)


def load_json(resource_listing, processors=None):
    loader = Loader(processors)
    return loader.process_resource_listing(resource_listing)
