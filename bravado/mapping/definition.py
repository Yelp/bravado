from copy import copy
from functools import partial

from bravado import swagger_type
from bravado.mapping.docstring import docstring_property
from bravado.mapping.docstring import create_definition_docstring


def build_definitions(definitions_dict):
    """Builds the objects that hold data types produced and consumed by
    operations.

    https://github.com/swagger-api/swagger-spec/blob/master/versions/2.0.md#definitionsObject  # noqa

    :param definitions_dict: spec['definitions']
    :returns: dict where (name,value) = (definition name, definition type)
    """
    definitions = {}
    for definition_name, definition_dict in definitions_dict.iteritems():
        definitions[definition_name] = \
            create_definition_type(definition_name, definition_dict)
    return definitions


def create_definition_type(definition_name, definition_dict):
    """Create a dynamic class from the definition data defined in the swagger
    spec.

    The docstring for this class is dynamically generated because generating
    the docstring is relatively expensive, and would only be used in rare
    cases for interactive debugging in a REPL.

    :param definition_name: definition name
    :param definition_dict: json-like dict that describes a definition.
    :returns: dynamic type created with attributes, docstrings attached
    :rtype: type
    """
    props = definition_dict['properties']

    methods = dict(
        __doc__=docstring_property(partial(create_definition_docstring, props)),
        __eq__=lambda self, other: compare(self, other),
        __init__=lambda self, **kwargs: set_props(self, **kwargs),
        __repr__=lambda self: create_definition_repr(self),
        __dir__=lambda self: props.keys(),
        _flat_dict=lambda self: create_flat_dict(self),
        _swagger_types=swagger_type.get_swagger_types(props),
        _required=definition_dict.get('required'),
    )
    return type(definition_name, (object,), methods)


def compare(first, second):
    """Compares two definition types for equivalence.

    If a type composes another definition type, .__dict__ recurse on those
    and compare again on those dict values.

    :param first: generated definition type reference
    :type first: type
    :param second: generated definition type reference
    :type second: type
    :returns: True if equivalent, False otherwise
    """
    # TODO: make sure this has a unit test
    if not hasattr(second, '__dict__'):
        return False

    # Ignore any '_raw' keys
    def norm_dict(d):
        return dict((k, d[k]) for k in d if k != '_raw')

    return norm_dict(first.__dict__) == norm_dict(second.__dict__)


def set_props(definition, **kwargs):
    """Constructor for the generated type - assigns given or default values

    :param definition: generated definition type reference
    :type definition: type
    :param kwargs: attributes to override default values of constructor
    :type kwargs: dict
    """
    # TODO: make sure this has a unit test
    types = getattr(definition, '_swagger_types')
    arg_keys = kwargs.keys()
    for property_name, property_swagger_type in types.iteritems():
        swagger_py_type = swagger_type.swagger_to_py_type(
            property_swagger_type)
        # Assign all property values specified in kwargs
        if property_name in arg_keys:
            property_value = kwargs[property_name]
            arg_keys.remove(property_name)
        else:
            # If not in kwargs, provide a default value to the type
            property_value = swagger_type.get_instance(swagger_py_type)
        setattr(definition, property_name, property_value)
    if arg_keys:
        raise AttributeError(" %s are not defined for %s." % (arg_keys, definition))


def create_definition_repr(definition):
    """Generates the repr string for the definition.

    :param definition: generated definition type
    :type definition: type
    :returns: repr string for the definition
    """
    string = ""
    separator = ""
    for prop in getattr(definition, '_swagger_types').keys():
        string += ("%s%s=%r" % (separator, prop, getattr(definition, prop)))
        separator = ", "
    return "%s(%s)" % (definition.__class__.__name__, string)


def create_flat_dict(definition):
    """Generates __dict__ of the definition traversing recursively
    each of the list item of an array and calling it again.
    While __dict__ only converts it on one level.

    :param definition: generated definition type reference
    :type definition: type
    :returns: flat dict repr of the definition

    Example: ::

        Pet(id=3, name="Name", photoUrls=["7"], tags=[Tag(id=2, name='T')])

    converts to: ::

        {'id': 3,
         'name': 'Name',
         'photoUrls': ['7'],
         'tags': [{'id': 2,
                   'name': 'T'}
                 ]
         }
    """
    if not hasattr(definition, '__dict__'):
        return definition
    definition_dict = copy(definition.__dict__)
    for k, v in definition.__dict__.iteritems():
        if isinstance(v, list):
            definition_dict[k] = [create_flat_dict(x) for x in v if x is not None]
        elif v is None:
            # Remove None values from dict to avoid their type checking
            if definition._required and k in definition._required:
                raise AttributeError("Required field %s can not be None" % k)
            definition_dict.pop(k)
        else:
            definition_dict[k] = create_flat_dict(v)
    return definition_dict