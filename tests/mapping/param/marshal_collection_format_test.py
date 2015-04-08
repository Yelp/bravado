import pytest

from bravado.mapping.param import marshal_collection_format, COLLECTION_FORMATS


@pytest.fixture
def array_spec():
    return {
        'in': 'query',
        'type': 'array',
        'items': {
            'type': 'integer'
        }
    }


def test_defaults_to_csv(array_spec):
    assert '1,2,3' == marshal_collection_format(array_spec, [1, 2, 3])


def test_formats(array_spec):
    for fmt, sep in COLLECTION_FORMATS.iteritems():
        array_spec['collectionFormat'] = fmt
        result = marshal_collection_format(array_spec, [1, 2, 3])
        assert sep.join(['1', '2', '3']) == result


def test_multi_no_op_because_handled_by_http_client_lib(array_spec):
    array_spec['collectionFormat'] = 'multi'
    assert [1, 2, 3] == marshal_collection_format(array_spec, [1, 2, 3])
