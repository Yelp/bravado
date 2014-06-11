#
# Copyright (c) Yelp, Inc.
#

"""Code for checking the response from API. If correct, proceeds to convert
   it into Python class types
"""

import dateutil.parser
from datetime import datetime
import swagger_type


class SwaggerResponse(object):
    """Converts the API json response to Python class models
    """

    def __init__(self, response, _type, models):
        """Ctor

        :param response: JSON response
        :type response: dict
        :param _type: type against which the response is to be validated
        :type _type: str or unicode
        :param models: namedtuple which maps complex type string to py type
        :type models: namedtuple
        """
        self.response = response
        self._type = _type
        self.models = models

    def parse_object(self):
        """Wrapper to check and create Py instance of the model in one go
        """
        return self.check_response_format().create_object()

    def create_object(self):
        """Creates the object assuming the response is checked and valid

        :returns: instance of complex Py object or simple primitive object
        """
        if self.response is None:
            return
        if swagger_type.is_primitive(self._type) or \
                self._type == 'void':
            return self.response
        if swagger_type.is_array(self._type):
            return self.create_array_object()
        return self.create_complex_object()

    def check_primitive_type(self):
        """Validate primitive type response is of correct type
           Also converts swagger type to py type if needed
           eg. datetime
        """
        ptype = swagger_type.get_primitive_mapping(self._type)
        if ptype == datetime:
            self.response = dateutil.parser.parse(self.response)
        if not isinstance(self.response, ptype):
            raise TypeError("Type of %s should be in %r" % \
                (self.response, ptype))

    def check_array_type(self):
        """Validate array type response is actually array type
           Also recursively converts response array to list of sub py types
        """
        if self.response is None:
            raise TypeError("Response array found as null instead of empty")
        if self.response.__class__ is not list:
            raise TypeError("Response is supposed to be an array instead of" %
                    self.response.__class__.__name__)
        subitem_type = swagger_type.get_subtype_array(self._type)
        self.response = [SwaggerResponse(item, subitem_type, self.models).
                                                    check_response_format().response
                                                            for item in self.response]

    def create_array_object(self):
        """Creates sub array objects by recursive call to create_object()
           Assume the response is validated and correct
        """
        subitem_type = swagger_type.get_subtype_array(self._type)
        return [SwaggerResponse(item, subitem_type, self.models).create_object()
                        for item in self.response]

    def check_complex_type(self):
        """Checks all the fields in the complex type are of proper type
           All the required fields are present and no extra field is present
        """
        if not isinstance(self.response, dict):
            raise TypeError("Type for %s is expected to be object" % self.response)
        klass = getattr(self.models, self._type)
        required = list(klass._required) if klass._required else []
        for key in self.response.keys():
            if key in required:
                required.remove(key)
            if key not in klass._swagger_types.keys():
                raise TypeError("Type for '%s' was not defined in spec." % key)
            swagger_response = SwaggerResponse(self.response[key],
                                            klass._swagger_types[key], self.models)
            self.response[key] = swagger_response.check_response_format().response
        if required:
            raise AssertionError("These required fields not present: %s" %
                    required)

    def create_complex_object(self):
        """Creates empty instance of complex object and then fills it with attrs
           Assume the response is validated and correct
        """
        klass = getattr(self.models, self._type)
        instance = klass()
        for key in self.response.keys():
            _type = klass._swagger_types[key]
            swagger_response = SwaggerResponse(self.response[key], _type, self.models)
            val = swagger_response.create_object()
            setattr(instance, key, val)
        return instance

    def check_response_format(self):
        """Check the response as per the type of the response
           Returns self to allow chaining of methods
        """
        if self._type == 'void':
            if self.response:
                raise TypeError("Response %s is supposed to be empty" % self.response)
        elif swagger_type.is_primitive(self._type):
            self.check_primitive_type()
        elif swagger_type.is_array(self._type):
            self.check_array_type()
        else:
            self.check_complex_type()
        return self
