from copy import copy
from functools import partial

from bravado import swagger_type
from bravado.mapping.docstring import docstring_property
from bravado.mapping.docstring import create_model_docstring


def build_models(definitions_dict):
    """Builds the models contained in a #/definitions dict. This applies
    to more than just definitions - generalize later.

    :param definitions_dict: spec['definitions']
    :returns: dict where (name,value) = (model name, model type)
    """
    models = {}
    for model_name, model_dict in definitions_dict.iteritems():
        models[model_name] = create_model_type(model_name, model_dict)
    return models


def create_model_type(model_name, model_dict):
    """Create a dynamic class from the model data defined in the swagger
    spec.

    The docstring for this class is dynamically generated because generating
    the docstring is relatively expensive, and would only be used in rare
    cases for interactive debugging in a REPL.

    :param model_name: model name
    :param model_dict: json-like dict that describes a model.
    :returns: dynamic type created with attributes, docstrings attached
    :rtype: type
    """
    props = model_dict['properties']

    methods = dict(
        __doc__=docstring_property(partial(create_model_docstring, props)),
        __eq__=lambda self, other: compare(self, other),
        __init__=lambda self, **kwargs: set_props(self, **kwargs),
        __repr__=lambda self: create_model_repr(self),
        __dir__=lambda self: props.keys(),
        _flat_dict=lambda self: create_flat_dict(self),
        _swagger_types=swagger_type.get_swagger_types(props),
        _required=model_dict.get('required'),
    )
    return type(str(model_name), (object,), methods)


def compare(first, second):
    """Compares two model types for equivalence.

    TODO: If a type composes another model type, .__dict__ recurse on those
          and compare again on those dict values.

    :param first: generated model type
    :type first: type
    :param second: generated model type
    :type second: type
    :returns: True if equivalent, False otherwise
    """
    if not hasattr(first, '__dict__') or not hasattr(second, '__dict__'):
        return False

    # Ignore any '_raw' keys
    def norm_dict(d):
        return dict((k, d[k]) for k in d if k != '_raw')

    return norm_dict(first.__dict__) == norm_dict(second.__dict__)


def set_props(model, **kwargs):
    """Constructor for the generated type - assigns given or default values

    :param model: generated model type
    :type model: type
    :param kwargs: attributes to override default values of constructor
    :type kwargs: dict
    """
    types = getattr(model, '_swagger_types')
    arg_keys = kwargs.keys()
    for prop_name, prop_swagger_type in types.iteritems():
        python_type = swagger_type.swagger_to_py_type(prop_swagger_type)
        # Assign all property values specified in kwargs
        if prop_name in arg_keys:
            prop_value = kwargs[prop_name]
            arg_keys.remove(prop_name)
        else:
            # If not in kwargs, provide a default value to the type
            prop_value = swagger_type.get_instance(python_type)
        setattr(model, prop_name, prop_value)
    if arg_keys:
        raise AttributeError(" %s are not defined for %s." % (arg_keys, model))


def create_model_repr(model):
    """Generates the repr string for the model.

    :param model: generated model type
    :type model: type
    :returns: repr string for the model
    """
    string = ""
    separator = ""
    for prop in sorted(getattr(model, '_swagger_types').keys()):
        string += ("%s%s=%r" % (separator, prop, getattr(model, prop)))
        separator = ", "
    return "%s(%s)" % (model.__class__.__name__, string)


def create_flat_dict(model):
    """Generates __dict__ of the model traversing recursively
    each of the list item of an array and calling it again.
    While __dict__ only converts it on one level.

    :param model: generated model type reference
    :type model: type
    :returns: flat dict repr of the model

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
    if not hasattr(model, '__dict__'):
        return model
    model_dict = copy(model.__dict__)
    for k, v in model.__dict__.iteritems():
        if isinstance(v, list):
            model_dict[k] = [create_flat_dict(x) for x in v if x is not None]
        elif v is None:
            # Remove None values from dict to avoid their type checking
            if model._required and k in model._required:
                raise AttributeError("Required field %s can not be None" % k)
            model_dict.pop(k)
        else:
            model_dict[k] = create_flat_dict(v)
    return model_dict
