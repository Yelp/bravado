Changelog-Master
================

- Add HTTP proxy support for requests client via Bravado config

Allow client to access resources for tags which have a space in them, by adding the `SwaggerClient.get_resource` method. For example, `client.get_resource('My Pets).list_pets().result()`.