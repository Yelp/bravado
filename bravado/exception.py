# -*- coding: utf-8 -*-

#
# Copyright (c) 2015, Yelp, Inc.
#


class HTTPError(IOError):
    """Initialize HTTPError with 'response' and 'request' object
    """

    def __init__(self, *args, **kwargs):
        response = kwargs.pop('response', None)
        self.response = response
        # populate request either from args or from response
        self.request = kwargs.pop('request', None)
        if(response is not None and not self.request and
                hasattr(response, 'request')):
            self.request = self.response.request
        super(HTTPError, self).__init__(*args, **kwargs)
