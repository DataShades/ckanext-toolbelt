from __future__ import annotations

from typing import Any

import pytest
from flask_login import encode_cookie  # pyright: ignore[reportUnknownVariableType]
from playwright.sync_api import BrowserContext, Page, expect

from ckan import types

expect.set_options(timeout=2000)


@pytest.fixture(autouse=True)
def page_timeout_(page: Page):
    """Reduce locator's timeout from 30s."""
    page.set_default_timeout(10000)


@pytest.fixture
def browser_context_args(browser_context_args: dict[str, Any], ckan_config: dict[str, Any]):
    """Modify playwright's standard configuration of browser's context."""
    browser_context_args["base_url"] = ckan_config["ckan.site_url"]
    return browser_context_args


@pytest.fixture
def login(page: Page, context: BrowserContext, ckan_config: types.FixtureCkanConfig, with_request_context: Any):
    """Provides a function for authentication by setting the remember cookie.

    Usage:
        def test_example(page: Page, login):
            login("testuser")
            page.goto("http://example.com/protected")

    This will set the remember cookie for 'testuser', allowing access to protected pages. To
    log out, call login with `None` or empty string, e.g., `login(None)`.
    """

    def authenticator(user: str | dict[str, Any], _page: Page | None = None):
        if _page is None:
            _page = page

        if isinstance(user, dict):
            user = user["name"]

        key = ckan_config["REMEMBER_COOKIE_NAME"]
        url = ckan_config["ckan.site_url"]

        if user:
            context.clear_cookies()
            context.add_cookies([{"name": key, "value": encode_cookie(user), "url": url}])
        else:
            context.clear_cookies()

    return authenticator
