from __future__ import annotations

from typing import Any

import ckan.plugins.toolkit as tk
from ckan import types


def {{ project_shortname }}_required(value: Any):
    """Verify that value is not empty."""
    if not value or value is tk.missing:
        raise tk.Invalid("Required")

    return value


def {{ project_shortname }}_complex_validator(
    key: types.FlattenKey,
    data: types.FlattenDataDict,
    errors: types.FlattenErrorDict,
    context: types.Context,
):
    """Verify that value is not empty."""
    if not data[key]:
        errors[key].append("Required")
        raise tk.StopOnError
