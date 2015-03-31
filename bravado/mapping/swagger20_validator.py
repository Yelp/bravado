from jsonschema import validators, _validators
from jsonschema.exceptions import ValidationError
from jsonschema.validators import Draft4Validator


def ignore(_validator, *args):
    """A validator which performs no validation. Used to `ignore` some schema
    fields during validation.
    """
    return


def required_validator(validator, req, instance, schema):
    """Swagger 2.0 expects `required` to be a bool in the Parameter object,
    but a list of properties everywhere else.
    """
    # TODO: Find a better way to identify if it is a Parameter schema
    if schema.get('in'):
        if req is True and not instance:
            return [ValidationError("%s is required" % schema['name'])]
    else:
        return _validators.required_draft4(validator, req, instance, schema)


def enum_validator(validator, enums, instance, schema):
    """Swagger 2.0 allows enums to be validated against objects of type
    arrays, like query parameter (collectionFormat: multi)
    """
    if schema.get('type') == 'array':
        return (v for item in instance for v in _validators.enum(
            validator, enums, item, schema))
    return _validators.enum(validator, enums, instance, schema)

Swagger20RequestValidator = validators.extend(
    Draft4Validator,
    {
        'required': required_validator,
        'enum': enum_validator,
    })
