Changelog-Master
================

*This file will contain the Changelog of the master branch.*

*The content will be used to build the Changelog of the new bravado release.*

Allow client to access resources for tags which have a space in them, by adding the `SwaggerClient.get_resource` method. For example, `client.get_resource('My Pets).list_pets().result()`.