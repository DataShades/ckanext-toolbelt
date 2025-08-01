from __future__ import annotations

from typing import Any

import pytest
from playwright.sync_api import expect, Page

expect.set_options(timeout=1000)


@pytest.fixture(autouse=True)
def page_timeout_(page: Page):
    """Reduce locator's timeout from 30s to 5s."""
    page.set_default_timeout(5000)


@pytest.fixture
def browser_context_args(
    browser_context_args: dict[str, Any], ckan_config: dict[str, Any]
):
    """Modify playwright's standard configuration of browser's context."""
    browser_context_args["base_url"] = ckan_config["ckan.site_url"]
    return browser_context_args


@pytest.fixture
def login(request: pytest.FixtureRequest, api_token_factory: Any, page: Page):
    """Provides a function for authentication."""

    def authenticator(user: str, _page: Page | None = None):
        if _page is None:
            _page = page

        token: str = api_token_factory(user=user)["token"]
        _page.set_extra_http_headers({"Authorization": token})

    return authenticator
