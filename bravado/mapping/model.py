from copy import copy
from functools import partial

from bravado import swagger_type
from bravado.mapping.docstring import docstring_property
from bravado.swagger_type import is_dict_like, is_list_like, \
    SWAGGER20_PRIMITIVES


# Models in #/definitions are tagged with this key so that they can be
# differentiated from 'object' types.
MODEL_MARKER = 'x-model'


def build_models(definitions_spec):
    """Builds the models contained in a #/definitions dict. This applies
    to more than just definitions - generalize later.

    :param definitions_spec: spec['definitions'] in dict form
    :returns: dict where (name,value) = (model name, model type)
    """
    models = {}
    for model_name, model_spec in definitions_spec.iteritems():
        # make models available under both simple name and $ref style name
        # - Pet <-- TODO: remove eventually
        # - #/definitions/Pet
        models[model_name] = create_model_type(model_name, model_spec)
        models['#/definitions/{0}'.format(model_name)] = models[model_name]
    return models


def create_model_type(model_name, model_spec):
    """Create a dynamic class from the model data defined in the swagger
    spec.

    The docstring for this class is dynamically generated because generating
    the docstring is relatively expensive, and would only be used in rare
    cases for interactive debugging in a REPL.

    :param model_name: model name
    :param model_spec: json-like dict that describes a model.
    :returns: dynamic type created with attributes, docstrings attached
    :rtype: type
    """
    props = model_spec['properties']

    methods = dict(
        __doc__=docstring_property(partial(create_model_docstring, model_spec)),
        __eq__=lambda self, other: compare(self, other),
        __init__=lambda self, **kwargs: model_constructor(self, model_spec,
                                                          kwargs),
        __repr__=lambda self: create_model_repr(self),
        __dir__=lambda self: props.keys(),
        _flat_dict=lambda self: create_flat_dict(self),        # TODO: remove
        _swagger_types=swagger_type.get_swagger_types(props),  # TODO: remove
        _required=model_spec.get('required'),                  # TODO: remove
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


def model_constructor(model, model_spec, constructor_kwargs):
    """Constructor for the given model instance. Just assigns kwargs as attrs
    on the model based on the 'properties' in the model specification.

    :param model: Instance of a model type
    :type model: type
    :param model_spec: model specification
    :type model_spec: dict
    :param constructor_kwargs: kwargs sent in to the constructor invocation
    :type constructor_kwargs: dict
    :raises: AttributeError on constructor_kwargs that don't exist in the
        model specification's list of properties
    """
    arg_names = constructor_kwargs.keys()

    for attr_name, attr_spec in model_spec['properties'].iteritems():
        if attr_name in arg_names:
            attr_value = constructor_kwargs[attr_name]
            arg_names.remove(attr_name)
        else:
            attr_value = None
        setattr(model, attr_name, attr_value)

    if arg_names:
        raise AttributeError(
            "Model {0} does not have attributes for: {1}"
            .format(type(model), arg_names))


def create_model_repr(model, model_spec):
    """Generates the repr string for the model.

    :param model: Instance of a model
    :param model_spec: model specification
    :type model_spec: dict
    :returns: repr string for the model
    """
    s = [
        "{0}={1}".format(attr_name, getattr(model, attr_name))
        for attr_name in sorted(model_spec['properties'].keys())
    ]
    return "{0}({1})".format(model.__class__.__name__, ', '.join(s))


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


def tag_models(spec_dict):
    # TODO: unit test + docstring
    # Tag #/definitions as being models with a 'x-model' key so that they can
    # be recognized after jsonref inlines $refs
    models_dict = spec_dict.get('definitions', {})
    for model_name, model_spec in models_dict.iteritems():
        model_type = model_spec.get('type')

        # default type type to 'object' since most swagger specs don't bother
        # to specify this
        if model_type is None:
            model_type = model_spec['type'] = 'object'

        # only tag objects. Not all #/definitions map to a Model type - can
        # be primitive or array, for example
        if model_type == 'object':
            model_spec[MODEL_MARKER] = model_name


def fix_malformed_model_refs(spec):
    """jsonref doesn't understand  { $ref: Category } so just fix it up to
    { $ref: #/definitions/Category } when the ref name matches a #/definitions
    name. Yes, this is hacky!

    :param spec: Swagger spec in dict form
    """
    # TODO: fix this in a sustainable way in a fork of jsonref and try to
    #       upstream
    # TODO: unit test
    model_names = [model_name for model_name in spec.get('definitions', {})]

    def descend(fragment):
        if is_dict_like(fragment):
            for k, v in fragment.iteritems():
                if k == '$ref' and v in model_names:
                    fragment[k] = "#/definitions/{0}".format(v)
                descend(v)
        elif is_list_like(fragment):
            for element in fragment:
                descend(element)

    descend(spec)


def is_model(spec):
    return MODEL_MARKER in spec


def create_model_docstring(model_spec):
    s = "Attributes:\n\n\t"
    attr_iter = iter(sorted(model_spec['properties'].iteritems()))
    # TODO: Add more stuff available in the spec - 'required', 'example', etc
    for attr_name, attr_spec in attr_iter:
        schema_type = attr_spec['type']

        if schema_type in SWAGGER20_PRIMITIVES:
            # TODO: update to python types and take 'format' into account
            attr_type = schema_type

        elif schema_type == 'array':
            array_spec = attr_spec['items']
            if is_model(array_spec):
                array_type = array_spec[MODEL_MARKER]
            else:
                array_type = array_spec['type']
            attr_type = "list of {0}".format(array_type)

        elif is_model(attr_spec):
            attr_type = attr_spec[MODEL_MARKER]

        elif schema_type == 'object':
            attr_type = 'dict'

        s += "{0}: {1}".format(attr_name, attr_type)

        if attr_spec.get('description'):
            s += " - {0}".format(attr_spec['description'])

        s += '\n\t'
    return s
