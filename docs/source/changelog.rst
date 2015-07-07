Changelog
=========
0.7.10 (2015-07-07)
++++++++++++++++++
* Make request and response available as attrs on HTTPError

0.7.5 (2015-01-21)
++++++++++++++++++
* Handle request path parameters with spaces correctly
* Performance improvements for loading large api docs
* Misc bug fixes

0.7.4 (2014-12-11)
++++++++++++++++++
* Requests urlencode params as utf8
* Docs related to 0.7.2
* Declare utf-8 encoding for all files

0.7.3 (2014-12-11)
++++++++++++++++++
* request logging is now done on the debug level instead of
  info level.

0.7.2 (2014-12-11)
++++++++++++++++++
* Allow headers to be passed in the api_docs request

0.7.1 (2014-12-11)
++++++++++++++++++
* Requests no longer mutate clients


0.7.0 (2014-11-26)
++++++++++++++++++
* headers are no longer cached and required as part of async and
  http client setup.

0.6.0 (2014-10-30)
++++++++++++++++++
* format='date' params are now represented and passed as
  datetime.date objects instead of datetime.datetimes.

0.5.0 (2014-08-08)
++++++++++++++++++

* Allow form request parameters. (Uploading files is supported)
* Default Values are taken if parameter not provided.
* Detailed exception error is raised (containing server response)
* New Optional parameters to ``result()``: ``allow_null`` and ``raw_response``.
* Headers passed to HttpClient will be passed to ``/api-docs`` call as well.

0.4.0 (2014-07-15)
++++++++++++++++++

* Allow MultiDict params. (for query parameters with allowMultiple: True)
* Query Parameters with type ``array`` are not further allowed.
