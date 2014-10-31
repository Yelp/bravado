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
