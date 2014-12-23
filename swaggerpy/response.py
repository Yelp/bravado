# -*- coding: utf-8 -*-

#
# Copyright (c) Yelp, Inc.
#

"""Code for checking the response from API. If correct, it proceeds to convert
it into Python class types
"""
import sys

import swagger_type
from swagger_type import SwaggerTypeCheck
from swaggerpy.exception import CancelledError


DEFAULT_TIMEOUT_S = 5.0


def handle_response_errors(e, CustomError):
    if hasattr(e, 'response') and hasattr(e.response, 'text'):
        # e.args is a tuple, change to list for modifications
        args = list(e.args)
        args[0] += (' : ' + e.response.text)
        e.args = tuple(args)
    if CustomError:
        error_msg = type(e).__name__ + " : " + str(e)
        raise CustomError(error_msg), None, sys.exc_info()[2]
    else:
        raise e


class HTTPFuture(object):

    """A future which inputs HTTP params"""
    def __init__(self, http_client, request_params, postHTTP_callback):
        """Kicks API call for Asynchronous client

        :param http_client: instance with public methods:
            start_request(), wait(), cancel()
        :param request_params: dict containing API request parameters
        :param postHTTP_callback: function to callback on finish
        """
        self._http_client = http_client
        self._postHTTP_callback = postHTTP_callback
        # A request is an EventualResult in the async client
        self._request = self._http_client.start_request(request_params)
        self._cancelled = False

    def cancelled(self):
        """Checks if API is cancelled
        Once cancelled, it can't be resumed
        """
        return self._cancelled

    def cancel(self):
        """Try to cancel the API (meaningful for Asynchronous client)
        """
        self._cancelled = True
        self._http_client.cancel(self._request)

    def result(self, **kwargs):
        """Blocking call to wait for API response
        If API was cancelled earlier, CancelledError is raised
        If everything goes fine, callback registered is triggered with response

        :param timeout: timeout in seconds to wait for response
        :type timeout: integer
        :param allow_null: if True, allow null fields in response
        :type allow_null: boolean
        :param raw_response: if True, return raw response w/o any validations
        :type raw_response: boolean
        """
        timeout = kwargs.pop('timeout', DEFAULT_TIMEOUT_S)

        if self.cancelled():
            raise CancelledError()
        response = self._http_client.wait(self._request, timeout)
        try:
            response.raise_for_status()
        except Exception as e:
            handle_response_errors(e, self._http_client.raise_with)

        return self._postHTTP_callback(response, **kwargs)


class SwaggerResponse(object):
    """Converts the API json response to Python class models

    Example: ::

        API Response
            {
                "id": 1,
                "category": {
                    "name": "chihuahua"
                },
                "name": "tommy",
                "photoUrls": [
                    ""
                ],
                "tags": [
                    {
                        "name": "cute"
                    }
                ],
                "status": "available"
            }

    SwaggerResponse: ::

        Pet(category=Category(id=0L, name=u'chihuahua'),
            status=u'available', name=u'tommy',
            tags=[Tag(id=0L, name=u'cute')], photoUrls=[u''], id=1)

    """

    def __init__(self, response, type_, models, **kwargs):
        """Wrapper to check and construt swagger response instance from API response

        :param response: JSON response
        :type response: dict
        :param type_: type against which the response is to be validated
        :type type_: str or unicode
        :param models: namedtuple which maps complex type string to py type
        :type models: namedtuple
        """
        allow_null = kwargs.pop('allow_null', False)
        raw_response = kwargs.pop('raw_response', False)

        if raw_response:
            self.swagger_object = response
            return

        response = SwaggerTypeCheck("Response", response, type_, models,
                                    allow_null).value
        self.swagger_object = SwaggerResponseConstruct(response,
                                                       type_,
                                                       models).create_object()


class SwaggerResponseConstruct(object):

    def __init__(self, response, type_, models):
        """Ctor to set the params

        :param _response: JSON response
        :type _response: dict
        :param type_: type against which the response is to be validated
        :type type_: str or unicode
        :param models: namedtuple which maps complex type string to py type
        :type models: namedtuple
        """
        self._response = response
        self._type = type_
        self._models = models

    def create_object(self):
        """Only public method in the class

        Creates the object assuming the response is checked and valid

        :returns: instance of complex Py object or simple primitive object
        """
        if self._response is None:
            return
        if swagger_type.is_primitive(self._type) or self._type == 'void':
            return self._response
        if swagger_type.is_array(self._type):
            return self._create_array_object()
        return self._create_complex_object()

    def _create_array_object(self):
        """Creates array item objects by recursive call to create_object()
        Assume the response is validated and correct
        """
        array_item_type = swagger_type.get_array_item_type(self._type)
        return [SwaggerResponseConstruct(item,
                                         array_item_type,
                                         self._models
                                         ).create_object()
                for item in self._response]

    def _create_complex_object(self):
        """Creates empty instance of complex object and then fills it with attrs
        Assume the response is validated and correct
        """
        klass = getattr(self._models, self._type)
        instance = klass()
        setattr(instance, '_raw', self._response)
        for key in self._response.keys():
            type_ = klass._swagger_types.get(key)
            if type_ is None:
                # Ignore unrecognized keys.  They will still be accessible in
                # the '_raw' field if needed.
                continue
            swagger_response = SwaggerResponseConstruct(self._response[key],
                                                        type_,
                                                        self._models)
            val = swagger_response.create_object()
            setattr(instance, key, val)
        return instance
