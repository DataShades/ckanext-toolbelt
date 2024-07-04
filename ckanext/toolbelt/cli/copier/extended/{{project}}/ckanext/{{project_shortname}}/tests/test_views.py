"""Tests for views.py."""

import pytest

import ckan.plugins.toolkit as tk


@pytest.mark.usefixtures("with_plugins")
def test_{{project_shortname}}_blueprint(app):
    resp = app.get(tk.h.url_for("{{project_shortname}}.page"))
    assert resp.status_code == 200
    assert resp.body == "Hello, {{project_shortname}}!"
