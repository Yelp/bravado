import logging

from bravado.mapping.operation import Operation


log = logging.getLogger(__name__)


def build_resources(spec, http_client):
    """Transforms the REST resources in the json-like spec into rich :Resource:
    objects that have associated :Operation:s.

    :param spec: json-like spec in dict form
    :param http_client: an HTTP client used to perform requests
    :type  http_client: :class:`bravado.http_client.HttpClient`
    :returns: dict where (key,value) = (resource name, Resource instance)
    """
    resources = {}
    paths = spec['paths']
    for path_name, path_dict in paths:
        resources[path_name] = Resource.from_path(
            path_name,
            path_dict,
            spec['x_api_url'],
            http_client)

    return resources


class Resource(object):
    """Swagger resource, described in an API declaration.
    """

    def __init__(self, name, operations):
        log.debug(u"Building resource '%s'" % name)
        self._name = name
        self._operations = operations

    # XXX 1.2
    # @classmethod
    # def from_api_doc(cls, api_doc, http_client, base_path, url_base=None):
    #     """
    #     :param api_doc: api doc which defines this resource
    #     :type  api_doc: :class:`dict`
    #     :param http_client: a :class:`bravado.http_client.HttpClient`
    #     :param base_path: base url to perform api requests. Used to override
    #             the path provided in the api spec
    #     :param url_base: a url used as the base for resource definitions
    #             that include a relative basePath
    #     """
    #     declaration = api_doc['api_declaration']
    #     models = build_models(declaration.get('models', {}))
    #
    #     def build_operation(api_obj, operation):
    #         log.debug(u"Building operation %s.%s" % (
    #             api_obj.get('name'), operation['nickname']))
    #
    #         resource_base_path = declaration.get('basePath')
    #         url = get_resource_url(base_path, url_base, resource_base_path)
    #         url = url.rstrip('/') + api_obj['path']
    #         return Operation(url, operation, http_client, models)
    #
    #     operations = dict(
    #         (oper['nickname'], build_operation(api, oper))
    #         for api in declaration['apis']
    #         for oper in api['operations'])
    #     return cls(api_doc['name'], operations)

    @classmethod
    def from_path(cls, path_name, path_dict, api_url, http_client):
        """
        :param path_name: Path of the resource. ex: /pets, pets/{id},
        :param path_dict: json-like dict which defines the resource. The key
            is usually an http method (get, put, post, delete, options, head,
            patch)
        :param api_url: base URL used to service API requests
        :param http_client: a :class:`bravado.http_client.HttpClient`
        """
        # TODO: Fix for 2.0

        # XXX 1.2
        # declaration = api_doc['api_declaration']
        # models = build_models(declaration.get('models', {}))

        # TODO: path_name can be a non-http method: 'parameters'
        # TODO: path_name can be $ref

        def build_operation(http_method, operation_dict):
            log.debug(u"Building operation %s.%s" % (
                path_name, operation_dict['operationId']))

            # resource_base_path = declaration.get('basePath')
            # url = get_resource_url(base_path, url_base, resource_base_path)
            # url = url.rstrip('/') + api_obj['path']

            url = api_url + path_name

            # TODO: figure out where to get 'models' from
            return Operation(url, operation_dict, http_client, models=None)

        operations = {}
        for http_method, operation_dict in path_dict.items():
            operation = build_operation(http_method, operation_dict)
            operations[operation['nickname']] = operation

        return cls(path_name, operations)

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
        return op

    def __dir__(self):
        return self._operations.keys()