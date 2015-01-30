from mock import Mock

from bravado.mapping.resource import build_resources
from bravado.http_client import HttpClient


def test_empty():
    resources = build_resources({}, http_client=Mock(spec=HttpClient))
    print resources