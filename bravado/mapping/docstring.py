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
