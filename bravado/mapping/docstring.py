from bravado import swagger_type


class docstring_property(object):

    def __init__(self, func):
        self.func = func

    def __get__(self, _cls, _owner):
        return self.func()


def create_model_docstring(props):
    """Generates a docstring for the type from the props

    :param props: dict containing properties of the type
    :type props: dict
    :returns: Generated string

    Example: ::

        "Pet": {
            "id": "Pet",
            "properties": {
                "id": {
                    "type": "integer",
                    "format": "int64",
                    "description": "unique identifier for the pet",
                },
                "category": {
                    "$ref": "Category"
                },
                "name": {
                    "type": "string"
                },
                "status": {
                    "type": "string",
                    "description": "pet status in the store",
                }
            }
        }

    Result: ::

        Attributes:

            category (Category)
            status (str) : pet status in the store
            name (str)
            id (long) : unique identifier for the pet
    """
    types = swagger_type.get_swagger_types(props)
    docstring = "Attributes:\n\n\t"
    for prop in props.keys():
        py_type = swagger_type.swagger_to_py_type_string(types[prop])
        docstring += ("%s (%s) " % (prop, py_type))
        if props[prop].get('description'):
            docstring += ": " + props[prop]['description']
        docstring += '\n\t'
    return docstring


def operation_docstring_wrapper(operation):
    """
    Workaround for docstrings to work for operations in a sane way.

    Docstrings can only be specified for modules, classes, and functions. Hence,
    the docstring for an Operation is static as defined by the Operation class.
    To make the docstring for an Operation invocation work correctly, it has
    to be masquaraded as a function. The docstring will then be attached to the
    function which works quite nicely. Example in REPL:

    >> petstore = client.get_client('http://url_to_petstore/')
    >> pet = petstore.pet
    >> help(pet.getPetById)

    Help on function getPetById in module bravado.mapping.resource:

    getPetById(**kwargs)
        [GET] Find pet by ID

        Returns a pet when ID < 10.  ID > 10 or nonintegers will simulate API error conditions

        :param petId: ID of pet that needs to be fetched
        :type petId: integer
        :returns: 200: successful operation
        :rtype: #/definitions/Pet
        :returns: 400: Invalid ID supplied
        :returns: 404: Pet not found

    :param operation: :class:`Operation`
    :return: callable that executes the operation
    """
    def wrapper(**kwargs):
        return operation(**kwargs)

    wrapper.__doc__ = create_operation_docstring(operation)
    wrapper.__name__ = str(operation.operation_id)
    return wrapper


def create_operation_docstring(operation):
    """Builds a comprehensive docstring for an Operation.

    :param operation: :class:`bravado.mapping.operation.Operation`
    :rtype: str

    Example: ::

        client.pet.findPetsByStatus?

    Outputs: ::

        [GET] Finds Pets by status

        Multiple status values can be provided with comma seperated strings

        :param status: Statuses to be considered for filter
        :type status: str
        :param from_date: Start date filter
        :type from_date: str
        :rtype: list
    """
    print 'creating op docstring for %s' % operation.operation_id
    s = ""
    op_dict = operation.operation_dict
    is_deprecated = op_dict.get('deprecated', False)
    if is_deprecated:
        s += "** DEPRECATED **\n"

    summary = op_dict.get('summary')
    if summary:
        s += "[{0}] {1}\n\n".format(operation.http_method.upper(), summary)

    desc = op_dict.get('description')
    if desc:
        s += "{0}\n\n".format(desc)

    for param_dict in op_dict.get('parameters', []):
        s += create_param_docstring(param_dict)

    responses = op_dict.get('responses')
    for http_status_code, response_dict in iter(sorted(responses.iteritems())):
        response_desc = response_dict.get('description')
        s += ':returns: {0}: {1}\n'.format(http_status_code, response_desc)
        schema_dict = response_dict.get('schema')
        if schema_dict:
            s += ':rtype: {0}\n'.format(
                swagger_type.get_swagger_type(schema_dict))
    return s


def create_param_docstring(param_dict):
    """Builds the docstring for a parameters from its specification.

    :param param_dict: parameter spec in json-line dict form
    :rtype: str

    Example: ::
        :param status: Status to be considered for filter
        :type status: string
    """
    name = param_dict.get('name')
    desc = param_dict.get('description', 'Document your spec, yo!')
    default_value = param_dict.get('default')
    location = param_dict.get('in')

    s = ":param {0}: {1}".format(name, desc)
    if default_value is not None:
        s += " (Default: {0})".format(default_value)
    s += "\n"

    if location == 'body':
        param_type = swagger_type.get_swagger_type(param_dict.get('schema'))
    else:
        param_type = param_dict.get('type')
    s += ":type {0}: {1}\n".format(name, param_type)

    # TODO: Lot more stuff can go in here - see "Parameter Object" in 2.0 Spec.
    return s
