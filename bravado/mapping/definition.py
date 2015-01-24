

# XXX 2.0
def build_definitions(definitions_dict):
    """
    definition - An object to hold data types produced and consumed by operations.

    https://github.com/swagger-api/swagger-spec/blob/master/versions/2.0.md#definitionsObject

    :param definitions_dict: spec['definitions']
    :returns: dict where (name,value) = (definition name, Definition type)
    """
    definitions = {}
    for definition_name, definition_dict in definitions.iteritems():
        definitions[definition_name] = \
            create_definition_type(definition_name, definition_dict)
    return definitions


# XXX 2.0
def create_definition_type(definition_name, definition_dict):
    """Create a dynamic class from the definition data defined in the swagger
    spec.

    The docstring for this class is dynamically generated because generating
    the docstring is relatively expensive, and would only be used in rare
    cases for interactive debugging in a REPL.

    :param definition_name: definition name
    :param definition_dict: json-like dict that describes a definition.
        {
            definitions {
                $definition_name {
                    $definition_dict
                }
            }
        }
    :returns: dynamic type created with attributes, docstrings attached
    :rtype: type
    """
    props = definition_dict['properties']

    methods = dict(
        __doc__=docstring_property(partial(create_model_docstring, props)),
        __eq__=lambda self, other: compare(self, other),
        __init__=lambda self, **kwargs: set_props(self, **kwargs),
        __repr__=lambda self: create_model_repr(self),
        __dir__=lambda self: props.keys(),
        _flat_dict=lambda self: create_flat_dict(self),
        _swagger_types=swagger_type.get_swagger_types(props),
        _required=model.get('required'),
    )
    return type(definition_name, (object,), methods)


def compare(first, second):
    """Compares the two types for equivalence.

    If a type composes another model types, .__dict__ recurse on those
    and compares again on those dict values
    """
    # TODO: make sure this has a unit test
    if not hasattr(second, '__dict__'):
        return False

    # Ignore any '_raw' keys
    def norm_dict(d):
        return dict((k, d[k]) for k in d if k != '_raw')

    return norm_dict(first.__dict__) == norm_dict(second.__dict__)


def set_props(model, **kwargs):
    """Constructor for the generated type - assigns given or default values

       :param model: generated model type reference
       :type model: type
       :param kwargs: attributes to override default values of constructor
       :type kwargs: dict
    """
    # TODO: make sure this has a unit test
    types = getattr(model, '_swagger_types')
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
        setattr(model, property_name, property_value)
    if arg_keys:
        raise AttributeError(" %s are not defined for %s." % (arg_keys, model))
