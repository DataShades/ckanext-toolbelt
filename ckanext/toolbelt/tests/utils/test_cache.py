import pytest
from pytest_mock import MockerFixture

from ckanext.toolbelt.utils import cache


def mul2(v: int):
    return v * 2


def test_dont_cache():
    value = {}
    assert cache.DontCache(value).unwrap() is value


def test_default_key_strategy():
    key = cache.default_key_strategy(mul2, 10)
    assert key.startswith(b"test_cache:mul2")


def test_decoreate_key_strategy():
    key = cache.decorate_key_strategy(b"hello:")(mul2, 10)
    assert isinstance(key, bytes)
    assert key.startswith(b"hello:test_cache:mul2")


@pytest.mark.usefixtures("clean_cache")
class TestCache:
    def fun(self, v):
        return v + v

    def test_basic(self, mocker: MockerFixture):
        spy = mocker.spy(self, "fun")

        decorated = cache.Cache()(self.fun)
        spy.assert_not_called()

        assert decorated(10) == 20
        spy.assert_called_once_with(10)

        assert decorated(20) == 40
        spy.assert_called_with(20)

        assert decorated(10) == 20
        assert spy.call_count == 2

        decorated.reset(10)
        assert decorated(10) == 20
        assert spy.call_count == 3

        decorated.reset(20)
        assert decorated(10) == 20
        assert spy.call_count == 3
