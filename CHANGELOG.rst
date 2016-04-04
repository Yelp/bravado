Changelog
=========

8.1.0 (2016-04-04)
------------------
- Support for YAML Swagger specs - PR #198
- Remove pytest-mock dependency from requirements-dev.txt. No longer used and it was breaking the build.
- Requires bravado-core >= 4.2.2
- Fix unit test for default values getting sent in the request

8.0.1 (2015-12-02)
------------------
- Require twisted < 15.5.0 since Python 2.6 support was dropped

8.0.0 (2015-11-25)
------------------
- Support for recursive $refs
- Support for remote $refs e.g. Swagger 2.0 specs that span multiple json files
- Requires bravado-core 4.0.0 which is not backwards compatible (See its `CHANGELOG <http://bravado-core.readthedocs.org/en/latest/changelog.html>`_)
- Transitively requires swagger-spec-validator 2.0.2 which is not backwards compatible (See its `CHANGELOG <http://swagger-spec-validator.readthedocs.org/en/latest/changelog.html>`_)

7.0.0 (2015-10-23)
------------------
- Support per-request response_callbacks_ to enable ``SwaggerClient``
  decorators to instrument an ``IncomingResponse`` post-receive. This is a
  non-backwards compatible change iff you have implemented a custom
  ``HttpClient``. Consult the changes in signature to ``HttpClient.request()``
  and ``HttpFuture``'s constructor.
- Config option ``also_return_response`` is supported on a per-request basis.

.. _response_callbacks: configuration.html#per-request-configuration

6.1.1 (2015-10-19)
------------------
- Fix ``IncomingResponse`` subclasses to provide access to the http headers.
- Requires bravado-core >= 3.1.0

6.1.0 (2015-10-19)
------------------
- Clients can now access the HTTP response from a service call to access things
  like headers and status code. See `Advanced Usage`_

.. _`Advanced Usage`: advanced.html#getting-access-to-the-http-response

6.0.0 (2015-10-12)
------------------
- User-defined formats are no longer global. The registration mechanism has
  changed and is now done via configuration. See Configuration_

.. _Configuration: configuration.html

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
