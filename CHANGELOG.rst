Changelog
=========

6.0.0 (2015-10-12)
------------------
- User-defined formats are no longer global. The registration mechanism has
  changed and is now done via configuration. See `configuration <http://bravado.readthedocs.org/en/latest/configuration.html>`_.

5.0.0 (2015-08-27)
------------------
- Update ResourceDecorator to return an operation as a CallableOperation
  instead of a function wrapper (for the docstring). This allows further
  decoration of the ResourceDecorator.

4.0.0 (2015-08-10)
------------------
- Consistent bravado.exception.HTTPError now thrown from both Fido and Requests http clients.
- HTTPError refactored to contain an optional detailed message and Swagger response result.

3.0.0 (2015-08-03)
------------------
- Support passing in connect_timeout and timeout via _request_options to the Fido and Requests clients
- Timeout in HTTPFuture now defaults to None (wait indefinitely) instead of 5s. You should make sure
  any calls to http_future.result(..) without a timeout are updated accordingly.

2.1.0 (2015-07-20)
------------------
- Add warning for deprecated operations

2.0.0 (2015-07-13)
------------------
- Assume responsibility for http invocation (used to be in bravado-core)

1.1.0 (2015-07-06)
------------------
- Made bravado compatible with Py34

1.0.0 (2015-06-26)
------------------
- Fixed petstore demo link
- Pick up bug fixes from bravado-core 1.1.0

1.0.0-rc2 (2015-06-01)
----------------------
- Renamed ResponseLike to IncomingResponse to match bravado-core

1.0.0-rc1 (2015-05-13)
----------------------
- Initial version - large refactoring/rewrite of swagger-py 0.7.5 to support Swagger 2.0
