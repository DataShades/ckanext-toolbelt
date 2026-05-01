from __future__ import annotations

import ckan.plugins.toolkit as tk

ENABLE_EVAL = "ckanext.toolbelt.devel.enable_eval"


def enable_eval() -> bool:
    return tk.config[ENABLE_EVAL]
