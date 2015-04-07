from bravado.mapping.operation import log
from bravado.mapping.param import unmarshal_param


class RequestLike(object):
    """
    Define a common interface for bravado to interface with server side
    request objects.

    Subclasses are responsible for providing attrs for __required_attrs__.
    """
    __required_attrs__ = [
        'path',     # dict of URL path parameters
        'params',   # dict of parameters from the query string and request body.
        'headers',  # dict of request headers
    ]

    def __getattr__(self, name):
        """
        When an attempt to access a required attribute that doesn't exist
        is made, let the caller know that the type is non-compliant in its
        attempt to be `RequestList`. This is in place of the usual throwing
        of an AttributeError.

        Reminder: __getattr___ is only called when it has already been
                  determined that this object does not have the given attr.

        :raises: NotImplementedError when the subclass has not provided access
                to a required attribute.
        """
        if name in self.__required_attrs__:
            raise NotImplementedError(
                'This RequestLike type {0} forgot to implement an attr '
                'for `{1}`'.format(type(self), name))
        raise AttributeError(
            "'{0}' object has no attribute '{1}'".format(type(self), name))

    def json(self, **kwargs):
        """
        :return: request content in a json-like form
        :rtype: int, float, double, string, unicode, list, dict
        """
        raise NotImplementedError("Implement json() in {0}".format(type(self)))


def unmarshal_request(request, op):
    """Unmarshal Swagger request parameters from the passed in request like
    object.

    :type request: :class: `bravado.mapping.request.RequestLike`.
    :type op: :class:`bravado.mapping.operation.Operation`
    :returns: dict where (key, value) = (param_name, param_value)
    """
    request_data = {}
    for param_name, param in op.params.iteritems():
        param_value = unmarshal_param(param, request)
        request_data[param_name] = param_value

    log.debug("Swagger request_data: {0}".format(request_data))
    return request_data
