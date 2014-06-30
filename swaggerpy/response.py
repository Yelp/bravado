#
# Copyright (c) Yelp, Inc.
#

"""Code for checking the response from API. If correct, it proceeds to convert
it into Python class types
"""

from datetime import datetime

import dateutil.parser

import swagger_type


DEFAULT_TIMEOUT_S = 5.0


class HTTPFuture(object):
    """A future which inputs HTTP params"""
    def __init__(self, http_client, request_params, postHTTP_callback):
        self._http_client = http_client
        self._postHTTP_callback = postHTTP_callback
        self._http_client.setup(request_params)

    def __call__(self, timeout=DEFAULT_TIMEOUT_S):
        response = self._http_client.wait(timeout)
        response.raise_for_status()
        return self._postHTTP_callback(response)


class SwaggerResponse(object):
    """Converts the API json response to Python class models

    Example:
    API Response
        {
            "id": 1,
            "category": {
                "name": "chihuahua"
            },
            "name": "tommy",
            "photoUrls": [
                ""
            ],
            "tags": [
                {
                    "name": "cute"
                }
            ],
            "status": "available"
        }

    SwaggerResponse
    Pet(category=Category(id=0L, name=u'chihuahua'), status=u'available', name=u'tommy',
        tags=[Tag(id=0L, name=u'cute')], photoUrls=[u''], id=1)
    """

    def __init__(self, response, type_, models):
        """Wrapper to check and construt swagger response instance from API response

        :param response: JSON response
        :type response: dict
        :param type_: type against which the response is to be validated
        :type type_: str or unicode
        :param models: namedtuple which maps complex type string to py type
        :type models: namedtuple
        """
        response = SwaggerResponseCheck(response, type_, models).response
        self.swagger_object = SwaggerResponseConstruct(response,
                                                       type_,
                                                       models).create_object()


class SwaggerResponseCheck(object):
    """Initialization of the class checks for the validity of the API response.

    Also handles conversion of response to Python types if necessary
    Ex. "2014-06-10T23:49:54.728+0000" -> datetime(2014, 6, 10, 23, 49, 54, 728000, tzinfo=tzutc())

    Raises TypeError/AssertionError if validation fails
    """

    def __init__(self, response, type_, models):
        """Ctor to set params and then check the response

        :param response: JSON response
        :type response: dict
        :param type_: type against which the response is to be validated
        :type type_: str or unicode
        :param models: namedtuple which maps complex type string to py type
        :type models: namedtuple
        """
        self.response = response
        self._type = type_
        self._models = models
        self._check_response_format()

    def _check_response_format(self):
        """Check the response as per the type of the response
        Returns self to allow chaining of methods
        """
        if self._type == 'void':
            if self.response:
                raise TypeError("Response %s is supposed to be empty" % self.response)
        elif swagger_type.is_primitive(self._type):
            self._check_primitive_type()
        elif swagger_type.is_array(self._type):
            self._check_array_type()
        else:
            self._check_complex_type()

    def _check_primitive_type(self):
        """Validate primitive type response is of correct type
        Also converts swagger type to py type if needed eg. datetime
        """
        ptype = swagger_type.get_primitive_mapping(self._type)
        if ptype == datetime:
            self.response = dateutil.parser.parse(self.response)
        if not isinstance(self.response, ptype):
            raise TypeError("Type of %s should be in %r" % (
                self.response, ptype))

    def _check_array_type(self):
        """Validate array type response is actually array type
        Also recursively converts response array to list of item array types
        """
        if self.response is None:
            raise TypeError("Response array found as null instead of empty")
        if self.response.__class__ is not list:
            raise TypeError("Response is supposed to be an array instead of" %
                            self.response.__class__.__name__)
        array_item_type = swagger_type.get_array_item_type(self._type)
        self.response = [SwaggerResponseCheck(item, array_item_type, self._models).response
                         for item in self.response]

    def _check_complex_type(self):
        """Checks all the fields in the complex type are of proper type
        All the required fields are present and no extra field is present
        """
        if not isinstance(self.response, dict):
            raise TypeError("Type for %s is expected to be object" % self.response)
        klass = getattr(self._models, self._type)
        required = list(klass._required) if klass._required else []
        for key in self.response.keys():
            if key in required:
                required.remove(key)
            if key not in klass._swagger_types.keys():
                raise TypeError("Type for '%s' was not defined in spec." % key)
            self.response[key] = SwaggerResponseCheck(self.response[key],
                                                      klass._swagger_types[key],
                                                      self._models).response
        if required:
            raise AssertionError("These required fields not present: %s" % required)


class SwaggerResponseConstruct(object):

    def __init__(self, response, type_, models):
        """Ctor to set the params

        :param _response: JSON response
        :type _response: dict
        :param type_: type against which the response is to be validated
        :type type_: str or unicode
        :param models: namedtuple which maps complex type string to py type
        :type models: namedtuple
        """
        self._response = response
        self._type = type_
        self._models = models

    def create_object(self):
        """Only public method in the class

        Creates the object assuming the response is checked and valid

        :returns: instance of complex Py object or simple primitive object
        """
        if self._response is None:
            return
        if swagger_type.is_primitive(self._type) or self._type == 'void':
            return self._response
        if swagger_type.is_array(self._type):
            return self._create_array_object()
        return self._create_complex_object()

    def _create_array_object(self):
        """Creates array item objects by recursive call to create_object()
        Assume the response is validated and correct
        """
        array_item_type = swagger_type.get_array_item_type(self._type)
        return [SwaggerResponseConstruct(item,
                                         array_item_type,
                                         self._models
                                         ).create_object()
                for item in self._response]

    def _create_complex_object(self):
        """Creates empty instance of complex object and then fills it with attrs
        Assume the response is validated and correct
        """
        klass = getattr(self._models, self._type)
        instance = klass()
        for key in self._response.keys():
            type_ = klass._swagger_types[key]
            swagger_response = SwaggerResponseConstruct(self._response[key],
                                                        type_,
                                                        self._models)
            val = swagger_response.create_object()
            setattr(instance, key, val)
        return instance
