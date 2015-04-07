from bravado.mapping.unmarshal import unmarshal_schema_object
from bravado.mapping.validate import validate_schema_object
from bravado.mapping.exception import SwaggerMappingError


class ResponseLike(object):
    """
    Define a common interface for bravado to interface with client side
    response objects from various 3rd party libraries.

    Subclasses are responsible for providing attrs for __required_attrs__.
    """
    __required_attrs__ = [
        'status_code',  # int
        'text',  # str
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


def unmarshal_response(response, op):
    """Unmarshal the http response into a (status_code, value) based on the
    response specification.

    :type response: :class:`bravado.mapping.response.ResponseLike`
    :type op: :class:`bravado.mapping.operation.Operation`
    :returns: tuple of (status_code, value) where type(value) matches
        response_spec['schema']['type'] if it exists, None otherwise.
    """
    response_spec = get_response_spec(response.status_code, op)

    def has_content(response_spec):
        return 'schema' in response_spec

    if not has_content(response_spec):
        return response.status_code, None

    # TODO: Non-json response contents
    content_spec = response_spec['schema']
    content_value = response.json()
    if op.swagger_spec.config['validate_responses']:
        validate_schema_object(content_spec, content_value)
    result = unmarshal_schema_object(
        op.swagger_spec, content_spec, content_value)
    return response.status_code, result


def get_response_spec(status_code, op):
    """Given the http status_code of an operation invocation's response, figure
    out which response specification it maps to.

    #/paths/
        {path_name}/
            {http_method}/
                responses/
                    {status_code}/
                        {response}

    :type status_code: int
    :type op: :class:`bravado.mapping.operation.Operation`
    :return: response specification
    :rtype: dict
    :raises: SwaggerMappingError when the status_code could not be mapped to
        a response specification.
    """
    # We don't need to worry about checking #/responses/ because jsonref has
    # already inlined the $refs
    response_specs = op.op_spec.get('responses')
    default_response_spec = response_specs.get('default', None)
    response_spec = response_specs.get(str(status_code), default_response_spec)
    if response_spec is None:
        raise SwaggerMappingError(
            "Response specification matching http status_code {0} not found "
            "for {1}. Either add a response specifiction for the status_code "
            "or use a `default` response.".format(op, status_code))
    return response_spec