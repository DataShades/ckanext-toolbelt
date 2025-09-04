from __future__ import annotations

from typing import Any

import pytest
from playwright.sync_api import Page, expect

expect.set_options(timeout=1000)

__all__ = [
    "browser_context_args",
    "login",
    "wait_for_ckan",
    "goto",
]


@pytest.fixture
def browser_context_args(
    browser_context_args: dict[str, Any], ckan_config: dict[str, Any]
):
    """Modify playwright's standard configuration of browser's context."""
    browser_context_args["base_url"] = ckan_config["ckan.site_url"]
    return browser_context_args


@pytest.fixture
def login(api_token_factory: Any, page: Page):
    """Provides a function for authentication."""

    def authenticator(user: str, _page: Page | None = None):
        if _page is None:
            _page = page

        token: str = api_token_factory(user=user)["token"]
        _page.set_extra_http_headers({"Authorization": token})

    return authenticator


@pytest.fixture
def wait_for_ckan(page: Page):
    """Wait for CKAN JS to be initialized.

    Use after page.goto() if you need to interact with widgets that have
    data-module attribute.
    """

    def waiter(_page: Page | None = None):
        if _page is None:
            _page = page

        page.wait_for_function("() => window.ckan && window.ckan.SITE_ROOT")
        page.wait_for_timeout(200)

    return waiter


@pytest.fixture
def goto(wait_for_ckan: Any, page: Page):
    """Page transition with autowait for CKAN initialization."""

    def switcher(url: str, _page: Page | None = None, **kwargs: Any):
        if _page is None:
            _page = page

        result = page.goto(url, **kwargs)
        wait_for_ckan(page)

        return result

    return switcher
