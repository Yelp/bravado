import pytest

from bravado.mapping.spec import build_api_serving_url


@pytest.fixture
def origin_url():
    return 'http://www.foo.com:80/bar/api-docs'


def test_no_overrides(origin_url):
    spec = {}
    assert origin_url == build_api_serving_url(spec, origin_url)


def test_override_host(origin_url):
    spec = {'host': 'womble.com'}
    api_serving_url = build_api_serving_url(spec, origin_url)
    assert 'http://womble.com/bar/api-docs' == api_serving_url


def test_override_basepath(origin_url):
    spec = {'basePath': '/v1'}
    api_serving_url = build_api_serving_url(spec, origin_url)
    assert 'http://www.foo.com:80/v1' == api_serving_url


def test_override_scheme(origin_url):
    spec = {'schemes': ['https']}
    api_serving_url = build_api_serving_url(spec, origin_url)
    assert 'https://www.foo.com:80/bar/api-docs' == api_serving_url


def test_pick_preferred_scheme(origin_url):
    spec = {'schemes': ['http', 'https']}
    api_serving_url = build_api_serving_url(
        spec, origin_url, preferred_scheme='https')
    assert 'https://www.foo.com:80/bar/api-docs' == api_serving_url


def test_pick_origin_scheme_when_preferred_scheme_none(origin_url):
    spec = {'schemes': ['http', 'https']}
    api_serving_url = build_api_serving_url(spec, origin_url)
    assert 'http://www.foo.com:80/bar/api-docs' == api_serving_url


def test_preferred_scheme_not_available(origin_url):
    spec = {'schemes': ['https']}
    with pytest.raises(Exception) as excinfo:
        build_api_serving_url(spec, origin_url, preferred_scheme='ws')
    assert 'not supported' in str(excinfo.value)
