from __future__ import annotations

from typing import TYPE_CHECKING

import ckan.plugins as p
import ckan.plugins.toolkit as tk

if TYPE_CHECKING:
    from ckan.common import CKANConfig


class FdtScrollPlugin(p.SingletonPlugin):
    p.implements(p.IConfigurer, inherit=True)

    def update_config(self, config: CKANConfig):
        if tk.asbool(config.get("debug")):
            tk.add_template_directory(config, "templates")
