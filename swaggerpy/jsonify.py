#
# Copyright (c) 2013, Digium, Inc.
#


def jsonify(obj):
    if isinstance(obj, list):
        return [jsonify(x) for x in obj]
    elif isinstance(obj, dict):
        return Jsonified(obj)
    else:
        return obj


class Jsonified(object):
    """A thin object wrapper around JSON
    """

    def __init__(self, json):
        """ ctor

        @type json: dict
        @param json: JSON object (results from json.load)
        """
        self.json = json

    def __repr__(self):
        return "%s(%r)" % (self.__class__.__name__, self.__dict__)

    def __getattr__(self, name):
        if not name in self.json:
            raise AttributeError("Unknown field '%s' on %r" % (name, self))

        return jsonify(self.json[name])

    def __getitem__(self, item):
        return jsonify(self.json[item])

    def get_field(self, field_name):
        return jsonify(self.json.get(field_name))

    def get_field_names(self):
        """Returns a list of the field names for this JSON object.

        @return: List of field names
        """
        return self.json.keys()
