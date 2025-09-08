from __future__ import annotations

from typing import Any, cast

import pytest
from flask_login import encode_cookie  # pyright: ignore[reportUnknownVariableType]
from playwright.sync_api import BrowserContext, Page

from ckan import types

__all__ = ["browser_context_args", "login", "wait_for_ckan", "goto", "ckan_standard", "milestone_screenshot"]


@pytest.fixture(autouse=True)
def ckan_standard(request: pytest.FixtureRequest):
    node = cast(pytest.Function, request.node)
    standard = {feature for marker in node.iter_markers("ckan_standard") for feature in marker.args}
    non_standard = {feature for marker in node.iter_markers("ckan_non_standard") for feature in marker.args}

    conflict = standard & non_standard
    if conflict:
        pytest.skip(f"Non-standard implementation of {conflict}")


@pytest.fixture
def browser_context_args(browser_context_args: dict[str, Any], ckan_config: dict[str, Any]):
    """Modify playwright's standard configuration of browser's context."""
    browser_context_args["base_url"] = ckan_config["ckan.site_url"]
    return browser_context_args


@pytest.fixture
def token_login(api_token_factory: Any, page: Page):
    """Provides a function for authentication using API token."""

    def authenticator(user: str | dict[str, Any], _page: Page | None = None):
        if _page is None:
            _page = page

        if isinstance(user, dict):
            user = user["name"]

        token: str = api_token_factory(user=user)["token"] if user else ""

        _page.set_extra_http_headers({"Authorization": token})

    return authenticator


@pytest.fixture
def login(page: Page, context: BrowserContext, ckan_config: types.FixtureCkanConfig, with_request_context: Any):
    """Provides a function for authentication by setting the remember cookie."""

    def authenticator(user: str | dict[str, Any], _page: Page | None = None):
        if _page is None:
            _page = page

        if isinstance(user, dict):
            user = user["name"]

        key = ckan_config["REMEMBER_COOKIE_NAME"]
        url = ckan_config["ckan.site_url"]

        context.add_cookies([{"name": key, "value": encode_cookie(user), "url": url}])

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


@pytest.fixture
def milestone_screenshot(page: Page, request: pytest.FixtureRequest):
    """Fixture to take screenshots at significant steps in a test."""
    step = 1

    def func(name: str, _page: Page | None = None, **kwargs: Any):
        """Takes a screenshot and saves it to the test-results directory."""
        nonlocal step
        node = request.node  # pyright: ignore[reportUnknownVariableType]
        if _page is None:
            _page = page

        prefix: str = node.originalname[5:]  # pyright: ignore[reportUnknownVariableType]
        kwargs["path"] = f"test-results/{prefix}__{step:02d}_{name}.jpeg"
        step += 1
        return _page.screenshot(**kwargs, full_page=True)

    return func
