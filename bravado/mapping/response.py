class ResponseLike(object):
    """
    Define a common interface for bravado to interface with client side
    response objects from various 3rd party libraries.

    Subclasses are responsible for providing attrs for __required_attrs__.
    """
    __required_attrs__ = [
        'status_code',  # int
    ]

    def __getattr__(self, name):
        """
        When an attempt to access a required attribute that doesn't exist
        is made, let the caller know that the type is non-compliant in its
        attempt to be `ResponseLike`. This is in place of the usual throwing
        of an AttributeError.

        Reminder: __getattr___ is only called when it has already been
                  determined that this object does not have the given attr.

        :raises: NotImplementedError when the subclass has not provided access
                to a required attribute.
        """
        if name in self.__required_attrs__:
            raise NotImplementedError(
                'This ResponseLike type {0} forgot to implement an attr '
                'for `{1}`'.format(type(self), name))
        raise AttributeError(
            "'{0}' object has no attribute '{1}'".format(type(self), name))

    def json(self, **kwargs):
        """
        :return: response content in a json-like form
        :rtype: int, float, double, string, unicode, list, dict
        """
        raise NotImplementedError("Implement json() in {0}".format(type(self)))

    def text(self, **kwargs):
        """
        :return: raw response from the server
        :rtype: str
        """
        raise NotImplementedError("Implement text() in {0}".format(type(self)))
