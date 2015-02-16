from bravado.mapping.marshal import marshal_object


def test_simple(empty_swagger_spec):

    address_spec = {
        'type': 'object',
        'properties': {
            'number': {
                'type': 'number'
            },
            'street_name': {
                'type': 'string'
            },
            'street_type': {
                'type': 'string',
                'enum': [
                    'Street',
                    'Avenue',
                    'Boulevard']
            }
        }
    }

    address = {
        "number": 1600,
        "street_name": "Pennsylvania",
        "street_type": "Avenue"
    }

    result = marshal_object(empty_swagger_spec, address_spec, address)
    assert address == result

