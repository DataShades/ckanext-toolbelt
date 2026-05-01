from __future__ import annotations

from typing import Any

from ckan import types


def toolbelt_devel_eval(context: types.Context, data_dict: dict[str, Any]):
    """Only sysadmin can evaluate expressions."""
    return {"success": False}
