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
        """ctor

        @type json: dict
        @param json: JSON object (results from json.load)
        """
        self._json = json
        # recursively promote fields from the json object to this one
        for (field, value) in json.iteritems():
            setattr(self, field, jsonify(value))

    def __repr__(self):
        return "%s(%r)" % (self.__class__.__name__, self.__dict__)

    def __getitem__(self, item):
        """Allow subscript syntax.

        @param item: Field name to look up
        @return:
        """
        return getattr(self, item)

    def get_field_names(self):
        """Returns a list of the field names for this JSON object.

        @return: List of field names
        """
        return self.__dict__.keys()

    def items(self):
        return [(k,v) for (k, v) in self.__dict__.items() if k != '_json']
