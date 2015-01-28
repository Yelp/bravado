from bravado.mapping.model import create_flat_dict, create_model_type


def test_simple_model(user_model):
    expected = {
        'email': 'darwin@woof.com',
        'firstName': 'Darwin',
        'id': 999L,
        'lastName': 'Dog',
        'password': 'woof',
        'phone': '111-222-3333',
        'userStatus': 9,
        'username': 'darwin'
    }
    user = user_model(**expected)
    assert expected == create_flat_dict(user)


def test_non_model():
    assert 'foo' == create_flat_dict('foo')


def test_model_with_list():
    pet_dict = {
        'properties': {
            'photoUrls': {
                'type': 'array',
                'items': {
                    'type': 'string'
                }
            }
        }
    }
    pet_model = create_model_type('Pet', pet_dict)
    props = {'photoUrls': ['a', 'b', 'c']}
    pet = pet_model(**props)
    assert props == create_flat_dict(pet)
