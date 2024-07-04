"""Tests for auth.py."""

import pytest

import ckan.model as model
import ckan.tests.factories as factories
import ckan.tests.helpers as test_helpers


@pytest.mark.ckan_config("ckan.plugins", "{{project_shortname}}")
@pytest.mark.usefixtures("with_plugins", "clean_db")
def test_{{project_shortname}}_get_sum():
    user = factories.User()
    context = {
        "user": user["name"],
        "model": model,
    }
    assert test_helpers.call_auth("{{project_shortname}}_get_sum", context=context)
