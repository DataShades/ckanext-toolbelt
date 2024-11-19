"""Tests for ckanext.{{ cookiecutter.project_shortname }}.logic.action."""

from __future__ import annotations

from typing import Any

import pytest

import ckan.model as model
import ckan.plugins.toolkit as tk
from ckan.tests.helpers import call_auth


@pytest.mark.ckan_config("ckan.plugins", "{{ cookiecutter.project_shortname }}")
@pytest.mark.usefixtures("with_plugins")
class TestGetSum:
    def test_anon_access(self):
        """Anonymous user can get sum."""
        assert call_auth(
            "{{ cookiecutter.project_shortname }}_get_sum",
            context={"model": model, "user": ""},
        )

    def test_authenticated_access(self, user: dict[str, Any]):
        """Authenticated user can get sum."""
        assert call_auth(
            "{{ cookiecutter.project_shortname }}_get_sum",
            context={"model": model, "user": user["name"]},
        )


@pytest.mark.ckan_config("ckan.plugins", "{{ cookiecutter.project_shortname }}")
@pytest.mark.usefixtures("with_plugins", "clean_db")
class TestCreateSomething:
    def test_anon_access(self):
        """Anonymous user cannot create something."""
        with pytest.raises(tk.NotAuthorized):
            call_auth(
                "{{ cookiecutter.project_shortname }}_something_create",
                context={"model": model, "user": ""},
            )

    def test_authenticated_access(self, user: dict[str, Any]):
        """Authenticated user can create something."""
        assert call_auth(
            "{{ cookiecutter.project_shortname }}_something_create",
            context={"model": model, "user": user["name"]},
        )
