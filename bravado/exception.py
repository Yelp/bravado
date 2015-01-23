#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
# Copyright (c) 2014, Yelp, Inc.
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


class CancelledError():
    """Error raised when result() is called from HTTPFuture
    and call was actually cancelled
    """


class SwaggerError(Exception):
    """Raised when an error is encountered mapping the JSON objects into the
    model.
    """

    def __init__(self, msg, context, cause=None):
        """Ctor.

        :param msg: String message for the error.
        :param context: ParsingContext object
        :param cause: Optional exception that caused this one.
        """
        super(Exception, self).__init__(msg, context, cause)