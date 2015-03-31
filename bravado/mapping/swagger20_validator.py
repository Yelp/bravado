from jsonschema import validators, _validators
from jsonschema.exceptions import ValidationError
from jsonschema.validators import Draft4Validator

from bravado.mapping.schema import is_param_spec

"""Draft4Validator is not completely compatible with Swagger 2.0 schema
objects like parameter, etc. Swagger20Validator is an extension of
Draft4Validator which customizes/wraps some of the operations of the default
validator.
"""


def ignore(_validator, *args):
    """A validator which performs no validation. Used to `ignore` some schema
    fields during validation.
    """
    return


def required_validator(validator, req, instance, schema):
    """Swagger 2.0 expects `required` to be a bool in the Parameter object,
    but a list of properties everywhere else.

    :param validator: Validator class used to validate the object
    :type validator: :class: `Swagger20Validator` or
                             `jsonschema.validators.Draft4Validator`
    :param req: value of `required` field
    :type req: boolean or list or None
    :param instance: object instance value
    :param schema: swagger spec for the object
    :type schema: dict
    """
    if is_param_spec(schema):
        if req is True and instance is None:
            return [ValidationError("%s is required" % schema['name'])]
    else:
        return _validators.required_draft4(validator, req, instance, schema)


def enum_validator(validator, enums, instance, schema):
    """Swagger 2.0 allows enums to be validated against objects of type
    arrays, like query parameter (collectionFormat: multi)

    :param validator: Validator class used to validate the object
    :type validator: :class: `Swagger20Validator` or
                             `jsonschema.validators.Draft4Validator`
    :param enums: allowed enum values
    :type enums: list
    :param instance: enum instance value
    :param schema: swagger spec for the object
    :type schema: dict
    """
    if schema.get('type') == 'array':
        return (v for item in instance for v in _validators.enum(
            validator, enums, item, schema))
    return _validators.enum(validator, enums, instance, schema)

Swagger20Validator = validators.extend(
    Draft4Validator,
    {
        'required': required_validator,
        'enum': enum_validator,
    })
