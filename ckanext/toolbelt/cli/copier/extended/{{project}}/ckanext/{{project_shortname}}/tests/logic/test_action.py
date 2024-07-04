"""Tests for action.py."""

import pytest

import ckan.tests.helpers as test_helpers


@pytest.mark.ckan_config("ckan.plugins", "{{project_shortname}}")
@pytest.mark.usefixtures("with_plugins")
def test_{{project_shortname}}_get_sum():
    result = test_helpers.call_action("{{project_shortname}}_get_sum", left=10, right=30)
    assert result["sum"] == 40
