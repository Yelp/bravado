# -*- coding: utf-8 -*-
"""Code for handling the base Swagger API model.
"""
from copy import copy
import logging
import os
import urllib
import urlparse

from swagger_spec_validator import validator20

from bravado import swagger_type
from bravado.compat import json
from bravado.http_client import SynchronousHttpClient


SWAGGER_VERSIONS = [u"1.2"]

log = logging.getLogger(__name__)


def is_file_scheme_uri(url):
    return urlparse.urlparse(url).scheme == u'file'


def json_load_file(url):
    # if '.json' isnt given, add it by default
    if not url.endswith('.json'):
        url += '.json'
    # requests can't handle file: scheme URLs
    fp = urllib.urlopen(url)
    try:
        return json.load(fp)
    finally:
        fp.close()


def json_load_url(http_client, url, headers):
    """Download and parse JSON from a URL.

    :param http_client: HTTP client interface.
    :type  http_client: http_client.HttpClient
    :param url: URL for JSON to parse
    :return: Parsed JSON dict
    """
    if is_file_scheme_uri(url):
        return json_load_file(url)
    else:
        request_params = {
            'method': 'GET',
            'url': url,
            'headers': headers,
        }
        req = http_client.start_request(request_params)
        resp = http_client.wait(req, timeout=None)
        return resp.json()


class Loader(object):
    """Abstraction for loading Swagger API's.

    :param http_client: HTTP client interface.
    :type  http_client: http_client.HttpClient
    """

    def __init__(self, http_client, api_doc_request_headers=None):
        self.http_client = http_client
        self.api_doc_request_headers = api_doc_request_headers or {}

    def load_spec(self, spec_url, base_url=None):
        """Load a Swagger Spec from the given URL

        :param spec_url: URL to swagger.json
        :param base_url: TODO: need this?
        :returns: validated json spec in dict form
        """
        spec_json = json_load_url(
            self.http_client,
            spec_url,
            self.api_doc_request_headers,
        )
        validator20.validate_spec(spec_json)
        return spec_json


def load_file(spec_file, http_client=None):
    """Loads and validates a Swagger spec file.

    :param http_client: HTTP client interface.
    :param spec_file: Path to swagger.json.
    :return: validated json spec in dict form
    :raise: IOError: On error reading swagger.json.
    """
    file_path = os.path.abspath(spec_file)
    url = urlparse.urljoin(u'file:', urllib.pathname2url(file_path))
    # When loading from files, everything is relative to the resource listing
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


def load_json(spec, http_client=None):
    """Process a swagger spec that has already been parsed.

    :param spec: Parsed Swagger spec.
    :type  spec: dict
    :param http_client:
    :return: validated spec in dict form
    """
    if http_client is None:
        http_client = SynchronousHttpClient()

    loader = Loader(http_client=http_client)
    loader.process_spec(spec)
    return spec


def create_model_type(model):
    """creates a dynamic model from the model data present in the json
       :param model: Resource Model json containing id, properties
       :type model: dict
       :returns: dynamic type created with attributes, docstrings attached
       :rtype: type
    """
    props = model['properties']
    name = str(model['id'])
    methods = dict(
        # Magic Methods :
        # Define the docstring
        __doc__=create_model_docstring(props),
        # Make equality work for dict & type OR type & type
        __eq__=lambda self, other: compare(self, other),
        # Define the constructor for the type
        __init__=lambda self, **kwargs: set_props(self, **kwargs),
        # Define the str repr of the type
        __repr__=lambda self: create_model_repr(self),
        # Instance methods :
        # Generates flat dict from the model instance
        _flat_dict=lambda self: create_flat_dict(self))
    model_type = type(name, (object,), methods)
    # Define a class variable to store types of its attributes
    setattr(model_type, '_swagger_types',
            swagger_type.get_swagger_types(props))
    # Define a class variable to store all required fields
    setattr(model_type, '_required', model.get('required'))
    return model_type


def set_props(model, **kwargs):
    """Constructor for the generated type - assigns given or default values

       :param model: generated model type reference
       :type model: type
       :param kwargs: attributes to override default values of constructor
       :type kwargs: dict
    """
    types = getattr(model, '_swagger_types')
    arg_keys = kwargs.keys()
    for property_name, property_swagger_type in types.iteritems():
        swagger_py_type = swagger_type.swagger_to_py_type(
            property_swagger_type)
        # Assign all property values specified in kwargs
        if property_name in arg_keys:
            property_value = kwargs[property_name]
            arg_keys.remove(property_name)
        else:
            # If not in kwargs, provide a default value to the type
            property_value = swagger_type.get_instance(swagger_py_type)
        setattr(model, property_name, property_value)
    if arg_keys:
        raise AttributeError(" %s are not defined for %s." % (arg_keys, model))


def create_model_docstring(props):
    """Generates a docstring for the type from the props

       :param props: dict containing properties of the type
       :type props: dict
       :returns: Generated string

    Example: ::

        "Pet": {
            "id": "Pet",
            "properties": {
                "id": {
                    "type": "integer",
                    "format": "int64",
                    "description": "unique identifier for the pet",
                },
                "category": {
                    "$ref": "Category"
                },
                "name": {
                    "type": "string"
                },
                "status": {
                    "type": "string",
                    "description": "pet status in the store",
                }
            }
        }

    Result: ::

        Attributes:

            category (Category)
            status (str) : pet status in the store
            name (str)
            id (long) : unique identifier for the pet
    """
    types = swagger_type.get_swagger_types(props)
    docstring = "Attributes:\n\n\t"
    for prop in props.keys():
        py_type = swagger_type.swagger_to_py_type_string(types[prop])
        docstring += ("%s (%s) " % (prop, py_type))
        if props[prop].get('description'):
            docstring += ": " + props[prop]['description']
        docstring += '\n\t'
    return docstring


def compare(first, second):
    """Compares the two types for equivalence.

    If a type composes another model types, .__dict__ recurse on those
    and compares again on those dict values
    """
    if not hasattr(second, '__dict__'):
        return False

    # Ignore any '_raw' keys
    def norm_dict(d):
        return dict((k, d[k]) for k in d if k != '_raw')

    return norm_dict(first.__dict__) == norm_dict(second.__dict__)


def create_flat_dict(model):
    """Generates __dict__ of the model traversing recursively
    each of the list item of an array and calling it again.
    While __dict__ only converts it on one level.

       :param model: generated model type reference
       :type model: type
       :returns: flat dict repr of the model

    Example: ::

        Pet(id=3, name="Name", photoUrls=["7"], tags=[Tag(id=2, name='T')])

    converts to: ::

        {'id': 3,
         'name': 'Name',
         'photoUrls': ['7'],
         'tags': [{'id': 2,
                   'name': 'T'}
                 ]
         }
    """
    if not hasattr(model, '__dict__'):
        return model
    model_dict = copy(model.__dict__)
    for k, v in model.__dict__.iteritems():
        if isinstance(v, list):
            model_dict[k] = [create_flat_dict(x) for x in v if x is not None]
        elif v is None:
            # Remove None values from dict to avoid their type checking
            if model._required and k in model._required:
                raise AttributeError("Required field %s can not be None" % k)
            model_dict.pop(k)
        else:
            model_dict[k] = create_flat_dict(v)
    return model_dict


def create_model_repr(model):
    """Generates the repr string for the model

       :param model: generated model type reference
       :type model: type
       :returns: repr string for the model
    """
    string = ""
    separator = ""
    for prop in getattr(model, '_swagger_types').keys():
        string += ("%s%s=%r" % (separator, prop, getattr(model, prop)))
        separator = ", "
    return ("%s(%s)" % (model.__class__.__name__, string))

