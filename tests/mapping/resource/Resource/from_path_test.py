from mock import Mock
import pytest

from bravado.http_client import HttpClient
from bravado.mapping.resource import Resource


@pytest.mark.xfail(reason='Revisit when Operation() working')
def test_simple(find_by_status_path_dict):

    resource = Resource.from_path(
        '/pet/findByStatus',
        find_by_status_path_dict,
        'http://localhost',
        http_client=Mock(spec=HttpClient))



