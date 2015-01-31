from mock import Mock
import pytest

from bravado.mapping.resource import build_resources
from bravado.http_client import HttpClient


def test_empty():
    spec = {
        'paths': {
        }
    }
    assert {} == build_resources(spec, http_client=Mock(spec=HttpClient))


@pytest.mark.xfail(reason='Enable when Resource.from_path(...) works')
def test_simple(paths_dict):
    spec = {
        'x_api_url': 'http://localhost',
        'paths': paths_dict
    }
    # TODO: Enable when Resource.from_path(...) works
    #resources = build_resources(spec, http_client=Mock(spec=HttpClient))
