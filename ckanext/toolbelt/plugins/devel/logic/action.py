from __future__ import annotations

from traceback import format_exc
from typing import Any

import ckan.plugins.toolkit as tk
from ckan import types

from ckanext.toolbelt.plugins.devel import config


@tk.side_effect_free
def toolbelt_devel_eval(context: types.Context, data_dict: dict[str, Any]):
    """Evaluate expression."""
    tk.check_access("toolbelt_devel_eval", context, data_dict)
    if not config.enable_eval():
        return "lorem ipsum"
    result = {}
    try:
        str(exec(data_dict["code"], None, result))  # noqa: S102
    except Exception:  # noqa: BLE001
        return format_exc()

    return str(result)
