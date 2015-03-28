#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
# Copyright (c) 2013, Digium, Inc.
# Copyright (c) 2014, Yelp, Inc.
#

DEFAULT_TIMEOUT_S = 5.0


class HttpFuture(object):
    """A future which inputs HTTP params"""

    def __init__(self, future, response_adapter, callback):
        """Kicks API call for Fido client

        :param future: future object
        :type future: :class: `concurrent.futures.Future`
        :param response_adapter: Adapter which exposes json(), status_code()
        :type response_adapter: :class: `bravado.mapping.response.ResponseLike`
        :param callback: Function to be called on the response
        """
        self.future = future
        self.response_adapter = response_adapter
        self.response_callback = callback

    def result(self, timeout=DEFAULT_TIMEOUT_S):
        """Blocking call to wait for API response

        :param timeout: Timeout in seconds for which client will get blocked
        to receive the response
        :return: Adapter response post callback
        """
        response = self.response_adapter(
            self.future.result(timeout=timeout))

        if self.response_callback:
            return self.response_callback(response)
        return response
