import logging
import urlparse

import jsonref
from swagger_spec_validator import validator20

from bravado.exception import SwaggerError
from bravado.mapping.model import build_models
from bravado.mapping.resource import build_resources
from bravado.mapping.model import tag_models
from bravado.mapping.model import fix_malformed_model_refs


log = logging.getLogger(__name__)


class Spec(object):
    """A Swagger API Specification.

    :param spec_dict: Swagger API specification in json-like dict form
    :param origin_url: URL from which the spec was retrieved.
    :param http_client: :class:`bravado.http_client.HTTPClient`
    """

    def __init__(self, spec_dict, origin_url=None, http_client=None):
        self.spec_dict = spec_dict
        self.origin_url = origin_url or 'unknown'
        self.http_client = http_client
        self.api_url = None

        # (key, value) = (simple format def name, Model type)
        # (key, value) = (#/ format def ref, Model type)
        self.definitions = None

        # (key, value) = (simple resource name, Resource)
        # (key, value) = (#/ format resource ref, Resource)
        self.resources = None

        # (key, value) = (simple ref name, param_spec in dict form)
        # (key, value) = (#/ format ref name, param_spec in dict form)
        self.params = None

        self.responses = None

    @classmethod
    def from_dict(cls, spec_dict, origin_url=None, http_client=None):
        """
        Build a :class:`Spec` from Swagger API Specificiation

        :param spec_dict: swagger spec in json-like dict form.
        :param origin_url: the url used to retrieve the spec, if any
        :type  origin_url: str
        """
        tag_models(spec_dict)
        fix_malformed_model_refs(spec_dict)
        spec_dict = jsonref.JsonRef.replace_refs(spec_dict)
        spec = cls(spec_dict, origin_url, http_client)
        spec.build()
        return spec

    def build(self):
        validator20.validate_spec(self.spec_dict)
        self.api_url = build_api_serving_url(self.spec_dict, self.origin_url)
        self.definitions = build_models(self.spec_dict['definitions'])
        #self.params = self.build_params()
        self.responses = self.build_responses()
        self.resources = build_resources(self)

    # def build_params(self):
    #     params = {}
    #     for ref_name, param_spec in self.spec_dict['parameters'].iteritems():
    #         # Register under both 'plain' ref name and #/ style ref name
    #         params[ref_name] = param_spec
    #         params['#/parameters/{0}'.format(ref_name)] = param_spec
    #     return params

    def build_responses(self):
        log.warn('TODO: implement Spec::build_responses()')
        return {}

    def resolve(self, object_spec):
        """Given an object specification, resolve the $ref if it is a $ref

        :param object_spec: object schema
        :return: dict
        :rtype: dict
        """
        if len(object_spec) == 1 and '$ref' in object_spec:
            # refs can be to
            # - #/parameters
            # - #/definitions
            # - #/responses
            #
            # TODO: consider tightening up the criteria by having the
            #       caller specify in which context the ref is valid.
            #       Search all for now
            ref_name = object_spec['$ref']
            if ref_name in self.params:
                return self.params[ref_name]
            if ref_name in self.definitions:
                return self.definitions[ref_name]
            if ref_name in self.responses:
                return self.responses[ref_name]
            raise SwaggerError('Cound not resolve $ref {0}'.format(ref_name))
        return object_spec

def build_api_serving_url(spec_dict, origin_url, preferred_scheme=None):
    """The URL used to service API requests does not necessarily have to be the
    same URL that was used to retrieve the API spec_dict.

    The existence of three fields in the root of the specification govern
    the value of the api_serving_url:

    - host string
        The host (name or ip) serving the API. This MUST be the host only and
        does not include the scheme nor sub-paths. It MAY include a port.
        If the host is not included, the host serving the documentation is to
        be used (including the port). The host does not support path templating.

    - basePath string
        The base path on which the API is served, which is relative to the
        host. If it is not included, the API is served directly under the host.
        The value MUST start with a leading slash (/). The basePath does not
        support path templating.

    - schemes [string]
        The transfer protocol of the API. Values MUST be from the list:
        "http", "https", "ws", "wss". If the schemes is not included,
        the default scheme to be used is the one used to access the
        specification.

    See https://github.com/swagger-api/swagger-spec_dict/blob/master/versions/2.0.md#swagger-object-   # noqa

    :param spec_dict: the Swagger spec in json-like dict form
    :param origin_url: the URL from which the spec was retrieved, if any
    :param preferred_scheme: preferred scheme to use if more than one scheme is
        supported by the API.
    :return: base url which services api requests
    """
    origin = urlparse.urlparse(origin_url)

    def pick_a_scheme(schemes):
        if not schemes:
            return origin.scheme

        if preferred_scheme:
            if preferred_scheme in schemes:
                return preferred_scheme
            raise Exception(
                "Preferred scheme {0} not supported by API. Available schemes "
                "include {1}".format(preferred_scheme, schemes))

        if origin.scheme in schemes:
            return origin.scheme

        if len(schemes) == 1:
            return schemes[0]

        raise Exception(
            "Origin scheme {0} not supported by API. Available schemes "
            "include {1}".format(origin.scheme, schemes))

    netloc = spec_dict.get('host', origin.netloc)
    path = spec_dict.get('basePath', origin.path)
    scheme = pick_a_scheme(spec_dict.get('schemes'))
    return urlparse.urlunparse((scheme, netloc, path, None, None, None))
