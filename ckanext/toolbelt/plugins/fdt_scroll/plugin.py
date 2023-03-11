from __future__ import annotations

import ckan.plugins as p
import ckan.plugins.toolkit as tk


class FdtScrollPlugin(p.SingletonPlugin):
    p.implements(p.IConfigurer, inherit=True)

    def update_config(self, config):
        if tk.asbool(tk.config.get("debug")):
            tk.add_template_directory(config, "templates")
