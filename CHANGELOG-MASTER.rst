Changelog-Master
================

*This file will contain the Changelog of the master branch.*

*The content will be used to build the Changelog of the new bravado release.*

Modified `RequestsClient`.

There is known [bug](https://github.com/requests/requests/issues/1906) in `requests` package which is still not fixed.

Basically it randomly raises `SSLError` when running multiple processes with same `Session`. We fixed it in out project
with little hack of yours class. If we create new session per request, the bug is gone.

Therefore I want to add option to `RequestsClient` for creating new `Session` per request.
