"""Tests for UI."""

from __future__ import annotations

import pytest
from playwright.sync_api import Page

import ckan.plugins.toolkit as tk


@pytest.mark.playwright
def test_homepage(page: Page):
    """Homepage shows about link."""
    page.goto(tk.url_for("home.index"))
    assert page.get_by_text("about").count()
