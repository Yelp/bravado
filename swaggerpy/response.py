import dateutil.parser
from datetime import datetime
import swagger_type


class SwaggerResponse(object):
    def __init__(self, response, _type, models):
        self.response = response
        self._type = _type
        self.models = models

    def parse_object(self):
        return self.check_response_format().create_object()

    def create_object(self):
        if self.response is None:
            return
        if swagger_type.is_primitive(self._type):
            return self.response
        if swagger_type.is_array(self._type):
            return self.create_array_object()
        return self.create_complex_object()

    def check_primitive_type(self):
        ptype = swagger_type.PRIMITIVE_TYPE_MAPPING[self._type]
        if ptype == datetime:
            self.response = dateutil.parser.parse(self.response)
        if not isinstance(self.response, ptype):
            raise TypeError("Type of %s should be %s" % \
                (self.response, ptype.__name__))

    def check_array_type(self):
        if self.response is None:
            raise TypeError("Response array found as null instead of empty")
        subitem_type = swagger_type.get_subtype_array(self._type)
        self.response = [SwaggerResponse(item, subitem_type, self.models).
                                                    check_response_format().response
                                                            for item in self.response]

    def create_array_object(self):
        subitem_type = swagger_type.get_subtype_array(self._type)
        return [SwaggerResponse(item, subitem_type, self.models).create_object()
                    if swagger_type.is_complex(subitem_type) else item
                        for item in self.response]

    def check_complex_type(self):
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
        klass = getattr(self.models, self._type)
        instance = klass()
        for key in self.response.keys():
            _type = klass._swagger_types[key]
            swagger_response = SwaggerResponse(self.response[key], _type, self.models)
            val = swagger_response.create_object() \
                       if swagger_type.is_complex(_type) else self.response[key]
            setattr(instance, key, val)
        return instance

    def check_response_format(self):
        if self.response is None:
            pass
        elif swagger_type.is_primitive(self._type):
            self.check_primitive_type()
        elif swagger_type.is_array(self._type):
            self.check_array_type()
        else:
            self.check_complex_type()
        return self
