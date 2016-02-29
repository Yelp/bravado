0.7.12 (2016-02-29)
------------------
- Fix JSON serializable error when datetime is passed in body

0.7.11 (2015-XX-XX)
------------------
- Require twisted < 15.5.0 since Python 2.6 support was dropped.

0.7.10 (2015-07-07)
------------------
- Make request and response available as attrs on HTTPError

0.7.5 (2015-01-21)
------------------
- Handle request path parameters with spaces correctly
- Performance improvements for loading large api docs
- Misc bug fixes

0.7.4 (2014-12-11)
------------------
- Requests urlencode params as utf8
- Docs related to 0.7.2
- Declare utf-8 encoding for all files

0.7.3 (2014-12-11)
------------------
- request logging is now done on the debug level instead of
  info level.

0.7.2 (2014-12-11)
------------------
- Allow headers to be passed in the api_docs request

0.7.1 (2014-12-11)
------------------
- Requests no longer mutate clients

0.7.0 (2014-11-26)
------------------
- headers are no longer cached and required as part of async and
  http client setup.

0.6.0 (2014-10-30)
------------------
- format='date' params are now represented and passed as
  datetime.date objects instead of datetime.datetimes.

0.5.7 (2014-10-23)
------------------
- Successfully validate objects that have additional fields beyond those
  specified in the associated model.
- Store raw deserialized JSON in '_raw' attribute of objects.
- Ignore '_raw' attribute in object equality checks.

0.2.0 (2013-10-28)
------------------
- Add close() methods to client and http_client.

0.1.0 (2013-10-24)
------------------

- Initial release
