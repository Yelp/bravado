from collections import defaultdict
import logging

from bravado.mapping.docstring import operation_docstring_wrapper
from bravado.mapping.operation import Operation

log = logging.getLogger(__name__)


def convert_path_to_resource(path_name):
    """
    Given a path name (#/paths/{path_name}) try to convert it into a resource
    name on a best effort basis when an operation has no tags.

    Examples:
      /pet                ->  pet
      /pet/findByStatus   ->  pet
      /pet/findByTags     ->  pet
      /pet/{petId}        ->  pet

    :param path_name: #/paths/{path_name} from a swagger spec
    :return: name of the resource to which operations under the given path
        should be associated with.
    """
    tokens = path_name.lstrip('/').split('/')
    err_msg = "Could not extract resource name from path {0}"
    if not tokens:
        raise Exception(err_msg.format(path_name))
    resource_name = tokens[0]
    if not resource_name:
        raise Exception(err_msg.format(path_name))
    return resource_name


def build_resources(swagger_spec):
    """Transforms the REST resources in the json-like swagger_spec into rich :Resource:
    objects that have associated :Operation:s.

    :type swagger_spec: :class:`bravado.mapping.spec.Spec`
    :returns: dict where (key,value) = (resource name, Resource)
    """
    # Map operations to resources using operation tags if available.
    # - If an operation has multiple tags, it will be associated with multiple
    #   resources!
    # - If an operation has no tags, its resource name will be derived from its
    #   path
    # key = tag_name   value = { operation_id : Operation }
    tag_to_operations = defaultdict(dict)
    paths = swagger_spec.spec_dict['paths']
    for path_name, path_dict in paths.iteritems():
        for http_method, operation_dict in path_dict.items():
            #operation = Operation(swagger_spec, path_name, http_method, operation_dict)
            operation = Operation.from_spec(swagger_spec, path_name, http_method, operation_dict)
            tags = operation_dict.get('tags', [])
            if not tags:
                tags.append(convert_path_to_resource(path_name))
            for tag in tags:
                tag_to_operations[tag][operation.operation_id] = operation

    resources = {}
    for tag, operations in tag_to_operations.iteritems():
        resources[tag] = Resource(tag, operations)
    return resources


class Resource(object):
    """Swagger resource, described in an API declaration.
    """

    def __init__(self, name, operations):
        log.debug(u"Building resource '%s'" % name)
        self._name = name
        self._operations = operations

    def __repr__(self):
        return u"%s(%s)" % (self.__class__.__name__, self._name)

    def __getattr__(self, item):
        """
        :param item: name of the :class:`Operation` to return
        :return: an :class:`Operation`
        """
        op = self._operations.get(item)
        if not op:
            raise AttributeError(u"Resource '%s' has no operation '%s'" %
                                 (self._name, item))
        return operation_docstring_wrapper(op)

    def __dir__(self):
        return self._operations.keys()
