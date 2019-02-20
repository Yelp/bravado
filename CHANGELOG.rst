Changelog
=========

10.3.0 (2019-02-20)
-------------------
- bravado is now fully type-annotated - PR #403
- Add ability to cancel a HttpFuture. Third-party HTTP clients will need to implement ``cancel`` on their :class:`.bravado.http_future.FutureAdapter` class to support this - PR #406
- The static method ``from_config_dict`` of :class:`.bravado.config.BravadoConfig` was removed due to compatibility issues with Python 3.5.0. This method was meant for internal use only; if you do happen to call it please switch to :func:`.bravado.config.bravado_config_from_config_dict` instead. - PR #407

10.2.2 (2019-01-03)
-------------------
- Fix issue with default (requests) HTTP client if HTTP_PROXY environment variable is set - Issue #401, PR #402. Thanks Lourens Veen for the initial report!

10.2.1 (2018-11-16)
-------------------
- Reraise network errors when unmarshalling - PR #397

10.2.0 (2018-10-19)
-------------------
- Support customizing or disabling SSL/TLS validation for the default HTTP client - Issues #278, #311, PR #392
- Use the fallback result in case of connection errors as well - PR #381

10.1.0 (2018-06-26)
-------------------
- Add support for non-callable fallback results, stabilize the response API - PR #376
- Add unified connection error handling support, introduce :class:`.bravado.exception.BravadoConnectionError` - PR #377
- Support per-request API key header overwriting - PR #374. Thanks Yuliya Bagriy for your contribution!
- Extract integration testing tools to :mod:`bravado.testing.integration_test` module - PR #378

10.0.1 (2018-06-20)
-------------------
- Add helper classes (in :mod:`bravado.testing.response_mocks`) for unit testing code using bravado - PR #375

10.0.0 (2018-06-15)
-------------------
- Re-add ability to force returning fallback results - PR #372. Per-request configuration is now handled by the
  new :class:`bravado.config.RequestConfig` class. This change requires an updated version of bravado-asyncio
  in case you're using that HTTP client.

9.3.2 (2018-06-15)
------------------
- Revert ability to force returning fallback results which was introduced in 9.3.1, since it contains
  backwards-incompatible changes that break third-party HTTP clients like bravado-asyncio.

9.3.1 (2018-06-14)
------------------
- Add ability to force returning fallback results - PR #372

9.3.0 (2018-06-05)
------------------
- Introduce the HTTPFuture.response API as well as support for returning a fallback result. - PR #365, #366, #367, #368

  *NOTE:* Most of this API is not documented yet and is considered experimental; we're working on stabilizing it
  and providing developer documentation.

9.2.2 (2017-12-19)
------------------
- Fix msgpack import issue - PR #341. Thanks Jesse Myers for your contribution!

9.2.1 (2017-12-07)
------------------
- The timeout exception for the requests client should inherit from ``requests.exceptions.ReadTimeout`` instead of ``requests.exceptions.Timeout`` - PR #337

9.2.0 (2017-11-10)
------------------
- Support msgpack as wire format for response data - PR #323, 328, 330, 331
- Allow client to access resources for tags which are not valid Python identifier names, by adding the ``SwaggerClient.get_resource`` method.
  For example, ``client.get_resource('My Pets').list_pets()`` - PR #320. Thanks Craig Blaszczyk for your contribution!
- Unify timeout exception classes. You can now simply catch ``bravado.exception.BravadoTimeoutError`` (or ``builtins.TimeoutError`` if you're using Python 3.3+) - PR #321

9.1.1 (2017-10-10)
------------------
- Allow users to pass the tcp_nodelay request parameter to FidoClient requests - PR #319

9.1.0 (2017-08-02)
------------------
- Make sure HTTP header names and values are unicode strings when using the fido HTTP client.
  NOTE: this is a potentially backwards incompatible change if you're using the fido HTTP client and
  are working with response headers. It's also highly advised to not upgrade to bravado-core 4.8.0+
  if you're using fido unless you're also upgrading to a bravado version that contains this change.

9.0.7 (2017-07-05)
------------------
- Require fido version 4.2.1 so we stay compatible to code catching crochet.TimeoutError

9.0.6 (2017-06-28)
------------------
- Don't mangle headers with bytestring values on Python 3

9.0.5 (2017-06-23)
------------------
- Make sure headers passed in for fetching specs are converted to str as well

9.0.4 (2017-06-22)
------------------
- Fix regression when passing swagger parameters of type header in ``_request_options`` introduced by PR #288

9.0.3 (2017-06-21)
------------------
- When using the fido HTTP client and passing a timeout to ``result()``, make sure we throw a fido HTTPTimeoutError instead of a crochet TimeoutError when hitting the timeout.

9.0.2 (2017-06-12)
------------------
- ``_requests_options`` headers are casted to ``string`` to support newer version of ``requests`` library.

9.0.1 (2017-06-09)
------------------
- Convert http method to str while constructing the request to fix an issue with file uploads when using requests library versions before 2.8.

9.0.0 (2017-06-06)
------------------
- Add API key authentication via header to RequestsClient.
- Fido client is now an optional dependency. **NOTE**: if you intend to use bravado with the fido client you need to install bravado with fido extras (``pip install bravado[fido]``)

8.4.0 (2016-09-27)
------------------
- Remove support for Python 2.6, fixing a build failure.
- Switch from Python 3.4 to Python 3.5 for tests.

8.3.0 (2016-06-03)
------------------
- Bravado using Fido 3.2.0 python 3 ready

8.2.0 (2016-04-29)
------------------
- Bravado compliant to Fido 3.0.0
- Dropped use of concurrent futures in favor of crochet EventualResult
- Workaround for bypassing a unicode bug in python `requests` < 2.8.1

8.1.2 (2016-04-18)
------------------
- Don't unnecessarily constrain the version of twisted when not using python 2.6

8.1.1 (2016-04-13)
------------------
- Removed logic to build multipart forms. Using python 'requests' instead to build the entire http request.

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
