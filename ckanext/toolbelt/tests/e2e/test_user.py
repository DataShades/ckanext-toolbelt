from __future__ import annotations

import pytest

from ckanext.toolbelt.tests.e2e_base.user import StandardUser


@pytest.mark.playwright
class TestStandard(StandardUser):
    pass
