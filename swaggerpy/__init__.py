#
# Copyright (c) 2013, Digium, Inc.
#

import swagger_model
import jsonify


def load(resource_listing_file, processors=None):
    """Loads a resource listing file, applying the given processors.

    @param resource_listing_file: File name for a resource listing.
    @param processors: List of SwaggerProcessors to apply to the resulting
                       resource.
    @return: Processed object model from
    @raise IOError: On error reading api-docs.
    """
    loader = swagger_model.Loader(processors)
    return loader.load_resource_listing(resource_listing_file)
