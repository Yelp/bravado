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


def _is_valid_field(field_name):
    return field_name != '_json'


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
        @return: the named field, or None
        """
        try:
            return getattr(self, item)
        except AttributeError:
            return None

    def __contains__(self, item):
        """Implement the 'in' keyword.

        @param item: Field name to look up
        @return: True if item names a field; False otherwise
        """
        return self[item] is not None

    def __iter__(self):
        """Allow iterator syntax
        """
        for kv in self.items():
            yield kv

    def get_field_names(self):
        """Returns a list of the field names for this JSON object.

        @return: List of field names
        """
        return filter(_is_valid_field, self.__dict__.keys())

    def items(self):
        return [(k, v) for (k, v) in self.__dict__.items()
                if _is_valid_field(k)]

    def values(self):
        return [v for (k, v) in self.items()]
