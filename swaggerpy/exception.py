#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
# Copyright (c) 2014, Yelp, Inc.
#
from requests.exceptions import HTTPError  # noqa


class CancelledError():
    """Error raised when result() is called from HTTPFuture
    and call was actually cancelled
    """


class SwaggerError(Exception):
    """Raised when an error is encountered mapping a response objects into a
    model.

    :param msg: String message for the error.
    :param context: ParsingContext object
    :param cause: Optional exception that caused this one.
    """

    def __init__(self, msg, context, cause=None):
        super(Exception, self).__init__(msg, context, cause)
