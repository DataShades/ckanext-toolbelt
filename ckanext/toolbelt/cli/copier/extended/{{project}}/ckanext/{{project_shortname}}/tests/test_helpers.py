"""Tests for ckanext.{{ project_shortname }}.helpers module.

You can either call helpers directly or use `tk.h` and `with_plugins` fixture
to register and call helpers. The former is simpler, the latter verifies that
helpers are registered.
"""

from __future__ import annotations

from ckanext.{{project_shortname}} import helpers


def test_hello():
    """Helper returns expected greeting."""
    assert helpers.{{
        project_shortname
    }}_hello() == "Hello, {{project_shortname}}!"
