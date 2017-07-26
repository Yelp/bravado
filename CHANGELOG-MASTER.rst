Changelog-Master
================

*This file will contain the Changelog of the master branch.*

*The content will be used to build the Changelog of the new bravado release.*

- Make sure HTTP header names and values are unicode strings when using the fido HTTP client.
  NOTE: this is a potentially backwards incompatible change if you're using the fido HTTP client and
  are working with response headers. It's also highly advised to not upgrade to bravado-core 4.8.0+
  if you're using fido unless you're also upgrading to a bravado version that contains this change.
