from bravado.mapping.resource import build_resources
from bravado.mapping.spec import Spec


def test_empty():
    spec_dict = {'paths': {}}
    spec = Spec(spec_dict)
    assert {} == build_resources(spec)


def test_resource_with_a_single_operation_associated_by_tag(paths_spec):
    spec_dict = {'paths': paths_spec}
    resources = build_resources(Spec(spec_dict))
    assert 1 == len(resources)
    assert resources['pet'].findPetsByStatus


def test_resource_with_a_single_operation_associated_by_path_name(paths_spec):
    # rename path so we know resource name will not be 'pet'
    paths_spec['/foo/findByStatus'] = paths_spec['/pet/findByStatus']
    del paths_spec['/pet/findByStatus']

    # remove tags on operation so path name is used to assoc with a resource
    del paths_spec['/foo/findByStatus']['get']['tags']

    spec_dict = {'paths': paths_spec}
    resources = build_resources(Spec(spec_dict))
    assert 1 == len(resources)
    assert resources['foo'].findPetsByStatus


def test_many_resources_with_the_same_operation_cuz_multiple_tags(paths_spec):
    tags = ['foo', 'bar', 'baz', 'bing', 'boo']
    paths_spec['/pet/findByStatus']['get']['tags'] = tags
    spec_dict = {'paths': paths_spec}
    resources = build_resources(Spec(spec_dict))
    assert len(tags) == len(resources)
    for tag in tags:
        assert resources[tag].findPetsByStatus
