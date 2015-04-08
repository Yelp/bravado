import pytest

from bravado.mapping.param import unmarshal_collection_format
from bravado.mapping.param import COLLECTION_FORMATS


@pytest.fixture
def array_spec():
    return {
        'name': 'biz_ids',
        'in': 'query',
        'type': 'array',
        'items': {
            'type': 'integer'
        },
        'collectionFormat': 'csv',
    }


def test_defaults_to_csv(array_spec):
    del array_spec['collectionFormat']
    assert [1, 2, 3] == unmarshal_collection_format(array_spec, '1,2,3')


def test_formats(array_spec):
    for fmt, sep in COLLECTION_FORMATS.iteritems():
        array_spec['collectionFormat'] = fmt
        param_value = sep.join(['1', '2', '3'])
        assert [1, 2, 3] == unmarshal_collection_format(array_spec, param_value)


def test_multi_no_op_because_handled_by_http_client_lib(array_spec):
    array_spec['collectionFormat'] = 'multi'
    assert [1, 2, 3] == unmarshal_collection_format(array_spec, [1, 2, 3])
