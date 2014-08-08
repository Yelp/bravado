Changelog
=========

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
