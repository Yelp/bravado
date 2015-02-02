import pytest

from bravado.mapping.resource import build_resources
from bravado.mapping.spec import Spec


def test_empty():
    spec_dict = {
        'paths': {
        }
    }
    spec = Spec(spec_dict)
    assert {} == build_resources(spec)


@pytest.mark.xfail(reason='Enable when Resource.from_path(...) works')
def test_simple(paths_dict):
    spec_dict = {
        'x_api_url': 'http://localhost',
        'paths': paths_dict
    }
    spec = Spec(spec_dict)
    # TODO: Enable when Resource.from_path(...) works
    #resources = build_resources(spec, http_client=Mock(spec=HttpClient))
