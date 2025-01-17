from __future__ import annotations

from typing import Any

import pytest
from playwright.sync_api import expect

expect.set_options(timeout=1000)


@pytest.fixture
def browser_context_args(
    browser_context_args: dict[str, Any], ckan_config: dict[str, Any]
):
    """Modify playwright's standard configuration of browser's context."""
    browser_context_args["base_url"] = ckan_config["ckan.site_url"]
    return browser_context_args
