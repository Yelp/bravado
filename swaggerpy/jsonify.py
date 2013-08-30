#
# Copyright (c) 2013, Digium, Inc.
#

"""A handy way for dealing with JSON in Python.

The jsonify() method will wrap a JSON object model making it easier to deal
with.

>>> import json
>>> j = jsonify(json.loads('{"foo": 1, "bar": { "array": [10, 9, 8]}}'))

Fields of a JSON object can be accessed simply using dot-notation. Arrays with
subscript syntax.

>>> j.foo
1
>>> j.bar.array[1]
9

If a field does not exist, it's an AttributeError.

>>> j.does_not_exist
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
AttributeError: 'Jsonified' object has no attribute 'does_not_exist'

Objects can also be referenced using subscript syntax. Fields that do not exist
return None.

>>> j['foo']
1
>>> print j['does_not_exist']
None

"""


def jsonify(obj):
    """Wraps parse JSON in in a Jsonify.
    """
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

        :type json: dict
        :param json: JSON object (results from json.load)
        """
        self._json = json
        # recursively promote fields from the json object to this one
        for (field, value) in json.iteritems():
            setattr(self, field, jsonify(value))

    def __repr__(self):
        return "%s(%r)" % (self.__class__.__name__, self.__dict__)

    def __getitem__(self, item):
        """Allow subscript syntax.

        :param item: Field name to look up
        :return: the named field, or None
        """
        try:
            return getattr(self, item)
        except AttributeError:
            return None

    def __contains__(self, item):
        """Implement the "in" keyword.

        :param item: Field name to look up
        :return: True if item names a field; False otherwise
        """
        return self[item] is not None

    def __iter__(self):
        """Allow iterator syntax
        """
        for kv in self.items():
            yield kv

    def __len__(self):
        """Allow len(jsonified)
        """
        return len(self.get_field_names())

    def get_field_names(self):
        """Returns a list of the field names for this JSON object.

        :return: List of field names
        """
        return filter(_is_valid_field, self.__dict__.keys())

    def items(self):
        return [(k, v) for (k, v) in self.__dict__.items()
                if _is_valid_field(k)]

    def values(self):
        return [v for (k, v) in self.items()]


def _is_valid_field(field_name):
    return field_name != '_json'
