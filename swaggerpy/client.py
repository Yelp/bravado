#
# Copyright (c) 2013, Digium, Inc.
# Copyright (c) 2014, Yelp, Inc.
#

"""Swagger client library.
"""

import logging
import os.path
import urllib
import time
from collections import namedtuple
from urlparse import urlparse

from peak.util.proxies import ObjectWrapper

import swagger_type
from swaggerpy.http_client import SynchronousHttpClient
from swaggerpy.processors import WebsocketProcessor, SwaggerProcessor
from swaggerpy.response import HTTPFuture, SwaggerResponse
from swaggerpy.swagger_model import create_model_type, Loader
from swaggerpy.swagger_type import SwaggerTypeCheck

log = logging.getLogger(__name__)

SWAGGER_SPEC_LIFETIME_S = 300


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
        for param in self._json.get(u'parameters', []):
            # TODO: No check on param value right now.
            # To be done similar to checkResponse in SwaggerResponse
            value = kwargs.pop(param[u'name'], None)
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

        def py_model_convert_callback(response):
            value = None
            type_ = swagger_type.get_swagger_type(self._json)
            # Assume status is OK,
            # as exception would have been raised otherwise
            # Validate the response if it is not empty.
            if response.text:
                # Validate and convert API response to Python model instance
                value = SwaggerResponse(
                    response.json(), type_, self._models).swagger_object
            return value
        return HTTPFuture(self._http_client,
                          request, py_model_convert_callback)


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
        # If basePath is root, use the basePath stored during init
        basePath = (self._basePath if decl[u'basePath'] == '/'
                    else decl[u'basePath'])
        uri = basePath + api[u'path']
        return Operation(uri, operation, self._http_client, self.models)


class SwaggerClient(ObjectWrapper):
    """Proxy class to core _SwaggerClient class. It acts as a wrapper
    on all attributes of _SwaggerClient & adds a check for api-docs freshness.
    The proxy contains a timestamp to indicate the last fetch time of api-docs.
    If the timestamp is older by SWAGGER_SPEC_LIFETIME_S seconds, api-docs are
    fetched again.

    CAVEAT: Refetching only works if proxy object itself is used as a
    long-lived instance. If any attribute out of the client is saved
    externally (as a variable) and used for api calls, refetching won't
    take place.

    tl;dr.
    RECOMMENDED:
    future = client.pet.getPetById(petId=42)

    NOT RECOMMENDED:
    resource = client.pet  # referencing attribute out of client - BAD.
    ...
    future = resource.getPetById(...)
    """

    # Required as per: https://pypi.python.org/pypi/ProxyTypes#wrappers
    __slots__ = ('args', 'kwargs', 'timeout_s', 'timestamp')

    def __init__(self, *args, **kwargs):
        """Constructor to internally create the core _SwaggerClient class
        It saves the arguments to refetch the client again after timeout.
        :param args: packed list of arguments to the ctor
        :param kwargs: packed dict of arguments to the ctor

        'timeout' can be passed to override default SWAGGER_SPEC_LIFETIME_S
        """
        self.args = args
        self.timeout_s = kwargs.pop('timeout', SWAGGER_SPEC_LIFETIME_S)
        self.kwargs = kwargs
        # Try to assign api-docs on initialization else assign to None
        try:
            self._assign_client()
        except Exception, e:
            ObjectWrapper.__init__(self, None)
            log.error(str(e))

    def _is_stale(self):
        """Check if init of SwaggerClient failed on the last attempt OR
        the last timestamp is older than the timeout
        """
        return (not self.__subject__ or
                self.timestamp + self.timeout_s < time.time())

    def _update_timestamp(self):
        """Update the instance timestamp to the current timestamp
        """
        self.timestamp = time.time()

    def _assign_client(self):
        """Fetches/Refetches the swagger client. Makes api-docs HTTP request
        to build the client. Passes the arguments stored from proxy ctor.
        """
        ObjectWrapper.__init__(self, _SwaggerClient(
            *self.args,
            **self.kwargs))
        # Update at the end when all of the above goes through successfully
        self._update_timestamp()

    def __getattr__(self, name):
        """Intercept the attribute call to SwaggerClient and preprend it with
        staleness check and client reload if necessary
        """
        if self._is_stale():
            self._assign_client()
        return getattr(self.__subject__, name)


class _SwaggerClient(object):
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

        # Load Swagger APIs always synchronously
        loader = Loader(
            SynchronousHttpClient(), [WebsocketProcessor(), ClientProcessor()])

        # url_or_resource can be url of type str,
        # OR a dict of resource itself.
        if isinstance(url_or_resource, (str, unicode)):
            log.debug(u"Loading from %s" % url_or_resource)
            self._api_docs = loader.load_resource_listing(url_or_resource)
            parsed_uri = urlparse(url_or_resource)
            basePath = "{uri.scheme}://{uri.netloc}".format(uri=parsed_uri)
        else:
            log.debug(u"Loading from %s" % url_or_resource.get(u'basePath'))
            self._api_docs = url_or_resource
            loader.process_resource_listing(self._api_docs)
            basePath = url_or_resource.get(u'basePath')

        self._resources = {}
        for resource in self._api_docs[u'apis']:
            self._resources[resource[u'name']] = Resource(
                resource, http_client, basePath)
            setattr(self, resource['name'],
                    self._get_resource(resource[u'name']))

    def __repr__(self):
        return u"%s(%s)" % (self.__class__.__name__,
                            self._api_docs.get(u'basePath'))

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

    Example: "  status (string) : Statuses to be considered for filter
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

    Example:
    client.pet.findPetsByStatus?

    "[GET] Finds Pets by status

    Multiple status values can be provided with comma seperated strings
    Args:
            status (string) : Statuses to be considered for filter
            from_date (string) : Start date filter
    Returns:
            array
    Raises:
            400: Invalid status value"
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
            # TODO: model instance is not valid right now
            #       Must be given as a json string in the body
            request['headers'] = {'content-type': 'application/json'}
    # TODO: accept 'header', 'form' in paramType
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
    pname = param['name']
    type_ = swagger_type.get_swagger_type(param)
    param_req_type = param['paramType']

    # Check the parameter value against its type
    SwaggerTypeCheck(value, type_, models)

    if param_req_type in ('path', 'query'):
        # Parameters in path, query need to be primitive/array types
        if swagger_type.is_complex(type_):
            raise TypeError("Param %s is in %s and not primitive" %
                            (pname, param_req_type))

        # If list, Turn list items into comma separated values
        if swagger_type.is_array(type_):
            value = u",".join(str(x) for x in value)

    # Add the parameter value to the request object
    if value:
        add_param_to_req(param, value, request)
    else:
        if param.get(u'required'):
            raise TypeError(u"Missing required parameter '%s'" % pname)
