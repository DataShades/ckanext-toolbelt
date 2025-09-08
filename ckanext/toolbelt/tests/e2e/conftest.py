from __future__ import annotations

from playwright.sync_api import expect

from ckanext.toolbelt.tests.e2e_base.conftest import *  # noqa: F403

expect.set_options(timeout=2000)
