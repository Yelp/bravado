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


def create_operation_docstring(json_):
    """Builds Operation docstring from the json dict

    :param json_: data to create docstring from
    :type json_: dict
    :returns: string giving meta info

    Example: ::

        client.pet.findPetsByStatus?

    Outputs: ::

        [GET] Finds Pets by status

        Multiple status values can be provided with comma seperated strings
        Args:
                status (string) : Statuses to be considered for filter
                from_date (string) : Start date filter
        Returns:
                array
        Raises:
                400: Invalid status value
    """
    docstring = ""
    if json_.get('summary'):
        docstring += ("[%s] %s\n\n" % (json_['method'], json_.get('summary')))
    docstring += (json_["notes"] + "\n") if json_.get("notes") else ''

    if json_["parameters"]:
        docstring += "Args:\n"
        for param in json_["parameters"]:
            docstring += _build_param_docstring(param)
    if json_.get('type'):
        docstring += "Returns:\n\t%s\n" % json_["type"]
    if json_.get('responseMessages'):
        docstring += "Raises:\n"
        for msg in json_.get('responseMessages'):
            docstring += "\t%s: %s\n" % (msg.get("code"), msg.get("message"))
    return docstring


def _build_param_docstring(param):
    """Builds param docstring from the param dict

    :param param: data to create docstring from
    :type param: dict
    :returns: string giving meta info

    Example: ::
        status (string) : Statuses to be considered for filter
        from_date (string) : Start date filter"
    """
    string = "\t" + param.get("name")
    type_ = param.get('$ref') or param.get('format') or param.get('type')
    if type_:
        string += (" (%s) " % type_)
    if param.get('description'):
        string += ": " + param["description"]
    return string + "\n"
