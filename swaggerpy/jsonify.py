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
        self.json = json


    def __getattr__(self, name):
        if not name in self.json:
            raise AttributeError("Unknown field '%s'" % name)

        return jsonify(self.json[name])
