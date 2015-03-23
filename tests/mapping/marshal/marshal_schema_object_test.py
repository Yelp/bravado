import copy

from bravado.mapping.marshal import marshal_schema_object
from bravado.mapping.spec import Spec


def test_dicts_can_be_used_instead_of_models(petstore_dict):
    petstore_spec = Spec.from_dict(petstore_dict)
    pet_spec = petstore_spec.spec_dict['definitions']['Pet']
    pet = {
        'id': 1,
        'name': 'Fido',
        'status': 'sold',
        'photoUrls': ['wagtail.png', 'bark.png'],
        'category': {
            'id': 200,
            'name': 'friendly',
        },
        'tags': [
            {'id': 99, 'name': 'mini'},
            {'id': 100, 'name': 'brown'},
        ],
    }
    expected = copy.deepcopy(pet)
    result = marshal_schema_object(petstore_spec, pet_spec, pet)
    assert expected == result
