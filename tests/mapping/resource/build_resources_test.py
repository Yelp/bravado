from bravado.mapping.resource import build_resources
from bravado.mapping.spec import Spec


def test_empty():
    spec_dict = {'paths': {}}
    spec = Spec(spec_dict)
    assert {} == build_resources(spec)


def test_resource_with_a_single_operation_associated_by_tag(paths_dict):
    spec_dict = {'paths': paths_dict}
    resources = build_resources(Spec(spec_dict))
    assert 1 == len(resources)
    assert resources['pet'].findPetsByStatus


def test_resource_with_a_single_operation_associated_by_path_name(paths_dict):
    # rename path so we know resource name will not be 'pet'
    paths_dict['/foo/findByStatus'] = paths_dict['/pet/findByStatus']
    del paths_dict['/pet/findByStatus']

    # remove tags on operation so path name is used to assoc with a resource
    del paths_dict['/foo/findByStatus']['get']['tags']

    spec_dict = {'paths': paths_dict}
    resources = build_resources(Spec(spec_dict))
    assert 1 == len(resources)
    assert resources['foo'].findPetsByStatus


def test_many_resources_with_the_same_operation_cuz_multiple_tags(paths_dict):
    tags = ['foo', 'bar', 'baz', 'bing', 'boo']
    paths_dict['/pet/findByStatus']['get']['tags'] = tags
    spec_dict = {'paths': paths_dict}
    resources = build_resources(Spec(spec_dict))
    assert len(tags) == len(resources)
    for tag in tags:
        assert resources[tag].findPetsByStatus

