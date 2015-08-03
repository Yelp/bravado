from mock import Mock
import pytest
from requests.sessions import Session

from bravado.requests_client import RequestsFutureAdapter


@pytest.fixture
def request():
    return dict(url='http://foo.com')


@pytest.fixture
def session():
    return Mock(spec=Session)


def test_no_timeouts(session, request):
    misc_options = {}
    future = RequestsFutureAdapter(session, request, misc_options)
    assert future.build_timeout(result_timeout=None) is None


def test_service_timeout_and_result_timeout_None(session, request):
    misc_options = dict(timeout=1)
    future = RequestsFutureAdapter(session, request, misc_options)
    assert future.build_timeout(result_timeout=None) == 1


def test_no_service_timeout_and_result_timeout_not_None(session, request):
    misc_options = {}
    future = RequestsFutureAdapter(session, request, misc_options)
    assert future.build_timeout(result_timeout=1) == 1


def test_service_timeout_lt_result_timeout(session, request):
    misc_options = dict(timeout=10)
    future = RequestsFutureAdapter(session, request, misc_options)
    assert future.build_timeout(result_timeout=11) == 11


def test_service_timeout_gt_result_timeout(session, request):
    misc_options = dict(timeout=11)
    future = RequestsFutureAdapter(session, request, misc_options)
    assert future.build_timeout(result_timeout=10) == 11


def test_service_timeout_None_result_timeout_not_None(session, request):
    misc_options = dict(timeout=None)
    future = RequestsFutureAdapter(session, request, misc_options)
    assert future.build_timeout(result_timeout=10) == 10


def test_service_timeout_not_None_result_timeout_None(session, request):
    misc_options = dict(timeout=10)
    future = RequestsFutureAdapter(session, request, misc_options)
    assert future.build_timeout(result_timeout=None) == 10


def test_both_timeouts_the_same(session, request):
    misc_options = dict(timeout=10)
    future = RequestsFutureAdapter(session, request, misc_options)
    assert future.build_timeout(result_timeout=10) == 10


def test_connect_timeout_and_idle_timeout(session, request):
    misc_options = dict(connect_timeout=1, timeout=11)
    future = RequestsFutureAdapter(session, request, misc_options)
    assert future.build_timeout(result_timeout=None) == (1, 11)


def test_connect_timeout_only(session, request):
    misc_options = dict(connect_timeout=1)
    future = RequestsFutureAdapter(session, request, misc_options)
    assert future.build_timeout(result_timeout=None) == (1, None)
