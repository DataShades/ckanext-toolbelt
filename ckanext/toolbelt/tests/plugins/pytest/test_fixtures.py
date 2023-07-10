from __future__ import annotations

import pytest

import ckan.plugins.core as pcore


@pytest.fixture()
def load_text_view():
    if not pcore.plugin_loaded("text_view"):
        pcore.load("text_view")


@pytest.mark.ckan_config("ckan.plugins", "image_view")
def test_with_plugins_unloads_all_plugin(load_text_view, with_plugins):
    assert pcore.plugin_loaded("image_view")
    assert not pcore.plugin_loaded("text_view")


@pytest.mark.ckan_config("ckan.plugins", "image_view")
def test_with_plugins_allows_adding_plugins_afterwards(with_plugins, load_text_view):
    assert pcore.plugin_loaded("image_view")
    assert pcore.plugin_loaded("text_view")
