from __future__ import annotations

from typing import Any

import ckan.plugins.toolkit as tk
from ckan.logic import validate
from ckan.types import Context

from . import schema


@tk.side_effect_free
@validate(schema.get_sum)
def {{project_shortname}}_get_sum(context: Context, data_dict: dict[str, Any]):
    """Produce a sum of left and right.

    Args:
        left: firt argument
        right: second argument

    Returns:
        operation details
    """

    tk.check_access("{{project_shortname}}_get_sum", context, data_dict)

    return {
        "left": data_dict["left"],
        "right": data_dict["right"],
        "sum": data_dict["left"] + data_dict["right"],
    }
