import pytest

from ckanext.toolbelt import decorators


def fun():
    pass


def test_availability():
    assert decorators.Collector()(fun)
    assert decorators.Cache()(fun)
