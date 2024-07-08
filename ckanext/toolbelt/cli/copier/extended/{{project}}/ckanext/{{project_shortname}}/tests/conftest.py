from __future__ import annotations

from typing import Any

import pytest


@pytest.fixture()
def clean_db(reset_db: Any, migrate_db_for: Any):
    reset_db()
    migrate_db_for("files")
