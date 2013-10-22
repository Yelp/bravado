#
# Copyright (c) 2013, Digium, Inc.
#

"""Swagger processing libraries.

More information on Swagger can be found `on the Swagger website
<https://developers.helloreverb.com/swagger/>`
"""

__all__ = ["client", "codegen", "processors", "swagger_model"]

from swagger_model import load_file, load_json, load_url, Loader
from processors import SwaggerProcessor, SwaggerError
