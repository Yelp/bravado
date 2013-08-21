#
# Copyright (c) 2013, Digium, Inc.
#

import swaggerpy


class SwaggerClient(object):
    def __init__(self, discovery_url):
        self.discovery_url = discovery_url
        self.api_docs = swaggerpy.load_file(discovery_url)

    def apis(self):
        assert False
