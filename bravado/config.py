# -*- coding: utf-8 -*-
import logging
from collections import namedtuple
from importlib import import_module


log = logging.getLogger(__name__)


CONFIG_DEFAULTS = {
    # See the constructor of :class:`bravado.http_future.HttpFuture` for an
    # in depth explanation of what this means.
    'also_return_response': False,
    # Kill switch to disable returning fallback results even if provided.
    'disable_fallback_results': False,
    'response_metadata_class': 'bravado.response.BravadoResponseMetadata',
}


REQUEST_OPTIONS_DEFAULTS = {
    # List of callbacks that are executed after the incoming response has been
    # validated and the swagger_result has been unmarshalled.
    #
    # The callback should expect two arguments:
    #   param : incoming_response
    #   type  : subclass of class:`bravado_core.response.IncomingResponse`
    #   param : operation
    #   type  : class:`bravado_core.operation.Operation`
    'response_callbacks': [],
}


class BravadoConfig(
    namedtuple(
        'BravadoConfig',
        'also_return_response, disable_fallback_results, response_metadata_class',
    )
):
    @staticmethod
    def from_config_dict(config):
        if config is None:
            config = {}
        bravado_config = {key: value for key, value in config.iteritems() if key in BravadoConfig._fields}
        bravado_config = dict(CONFIG_DEFAULTS, **bravado_config)
        return BravadoConfig(
            **bravado_config
        )


def _import_class(fully_qualified_class_str):
    try:
        module_name, class_name = fully_qualified_class_str.rsplit('.', 1)
        return getattr(import_module(module_name), class_name)
    except (ImportError, AttributeError, ValueError) as e:
        log.warning(
            'Error while importing \'{fully_qualified_class_str}\': '
            '{exception_class}: {exception_content}'.format(
                fully_qualified_class_str=fully_qualified_class_str,
                exception_class=type(e),
                exception_content=str(e),
            )
        )
        return None
