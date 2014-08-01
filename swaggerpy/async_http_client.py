#!/usr/bin/env python

#
# Copyright (c) 2014, Yelp, Inc.
#

"""Asynchronous HTTP client abstractions.
"""

from cStringIO import StringIO
import json
import logging
from uuid import uuid4
import urllib

import crochet

import twisted.internet.error
import twisted.web.client
from swaggerpy import http_client
from swaggerpy.exception import HTTPError
from twisted.internet import reactor
from twisted.internet.defer import Deferred
from twisted.internet.protocol import Protocol
from twisted.web.client import Agent
from twisted.web.client import FileBodyProducer
from twisted.web.http_headers import Headers

log = logging.getLogger(__name__)


class AsynchronousHttpClient(http_client.HttpClient):
    """Asynchronous HTTP client implementation.

    :param headers: headers to be sent with the requests
    :type headers: dict
    """

    def __init__(self, headers={}):
        self._headers = headers

    def setup(self, request_params):
        """Sets up the request params as per Twisted Agent needs.
        Sets up crochet and triggers the API request in background

        :param request_params: request parameters for API call
        :type request_params: dict
        """
        headers_forced = request_params.pop('headers_forced')
        self.request_params = {
            'method': str(request_params['method']),
            'bodyProducer': stringify_body(request_params),
            'headers': listify_headers(merge_headers(
                request_params.get('headers'), headers_forced)),
            'uri': str(request_params['url'] + '?' + urllib.urlencode(
                request_params['params'], True))
        }

        crochet.setup()
        self.eventual = self.fetch_deferred()

    def cancel(self):
        """Try to cancel the API call using crochet's cancel() API
        """
        self.eventual.cancel()

    def wait(self, timeout):
        """Requests based implemention with timeout

        :param timeout: time in seconds to wait for response
        :return: Requests response
        :rtype:  requests.Response
        """
        log.info(u"%s %s", self.request_params.get('method'),
                 self.request_params.get('uri'))
        # finished_resp is returned here
        # TODO: catch known exceptions and raise common exceptions
        return self.eventual.wait(timeout)

    @crochet.run_in_reactor
    def fetch_deferred(self):
        """The main core to start the reacter and run the API
        in the background. Also the callbacks are registered here
        """
        finished_resp = Deferred()
        agent = Agent(reactor)
        deferred = agent.request(**self.request_params)

        def response_callback(response):
            """Callback for response received from server, even 4XX, 5XX possible
            response param stores the headers and status code.
            It needs a callback method to be registered to store the response
            body which is provided using deliverBody
            """
            response.deliverBody(_HTTPBodyFetcher(self.request_params,
                                                  response, finished_resp))
        deferred.addCallback(response_callback)

        def response_errback(reason):
            """Error callback method like server not reachable or conn. refused

            :param reason: The reason why request failed
            :type reason: str
            """
            finished_resp.errback(reason)
        deferred.addErrback(response_errback)

        return finished_resp


class AsyncResponse():
    """AsyncResponse inherits from requests.Response
    to inherit methods like json(), raise_for_status()

    Remove the property text and content and make them as overridable attrs
    """
    def __init__(self, req, resp, data):
        self.request = req
        self.status_code = resp.code
        self.headers = dict(resp.headers.getAllRawHeaders())
        self.text = data

    def raise_for_status(self):
        """Raises stored `HTTPError`, if one occured.
        """

        http_error_msg = ''

        if 400 <= self.status_code < 500:
            http_error_msg = '%s Client Error' % self.status_code

        elif 500 <= self.status_code < 600:
            http_error_msg = '%s Server Error' % self.status_code

        if http_error_msg:
            raise HTTPError(http_error_msg, response=self)

    def json(self, **kwargs):
        return json.loads(self.text, **kwargs)


class _HTTPBodyFetcher(Protocol):
    """Class to receive callbacks from Twisted whenever
    response is available.

    Eventually AsyncResponse() is created on receiving complete response
    """
    def __init__(self, request, response, finished):
        self.buffer = StringIO()
        self.request = request
        self.response = response
        self.finished = finished

    def dataReceived(self, data):
        self.buffer.write(data)

    def connectionLost(self, reason):
        # Accepting PotentialDataLoss for servers with HTTP1.0
        # and not sending Content-Length in the header
        if reason.check(twisted.web.client.ResponseDone) or \
                reason.check(twisted.web.http.PotentialDataLoss):
            self.finished.callback(AsyncResponse(
                self.request, self.response, self.buffer.getvalue()))
        else:
            self.finished.errback(reason)


def add_lines(name, content, is_file, boundary, lines):
    """Add content to lines with proper format needed for multipart
    content type.

    :param name: name of the request parameter
    :param content: contents of the request parameter
    :param is_file: is the parameter a file type (for adding filename)
    :param boundary: a string to be added after each request param
    :param lines: content array being populated
    :return: updated content array
    """
    header = "Content-Disposition: form-data; name={0}".format(name)
    if is_file:
        header += "; filename={0}".format(name)
    lines.extend(["--" + boundary, header, "", content])
    return lines


def get_random_boundary():
    """A simple boundary generator
    """
    return uuid4().hex


def stringify_body(request_params):
    """Wraps the data using twisted FileBodyProducer
    """
    headers = request_params.get('headers', {}) or {}
    if('files' in request_params):
        boundary = get_random_boundary()
        lines = []
        for k, v in request_params.get('data', {}).items():
            add_lines(k, v, False, boundary, lines)
        for file_name, f in request_params['files'].items():
            add_lines(file_name, f.read(), True, boundary, lines)
        lines.extend(["--" + boundary + "--", ""])
        data = "\r\n".join(lines)
        content_type = http_client.MULT_FORM + "; boundary={0}".format(
            boundary)
        headers['content-type'] = content_type
        # Skip 'content-length' as it is generated by BodyProducer
    elif(headers.get('content-type') == http_client.APP_FORM):
        data = urllib.urlencode(request_params.get('data', {}))
    else:
        http_client.stringify_body(request_params)
        data = request_params.get('data')
    return FileBodyProducer(StringIO(data)) if data else None


def merge_headers(*args):
    """Merge headers with last overriding the previous
    """
    result = {}
    for header in args:
        if header:
            result.update(header)
    return result


def listify_headers(headers):
    """Twisted agent requires header values as lists
    """
    headers = headers or {}
    for key, val in headers.iteritems():
        if not isinstance(val, list):
            headers[key] = [val]
    return Headers(headers)
