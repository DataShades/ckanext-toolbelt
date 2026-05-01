from __future__ import annotations

from typing_extensions import override

import ckan.plugins as p
import ckan.plugins.toolkit as tk
from ckan import common


@tk.blanket.actions
@tk.blanket.auth_functions
@tk.blanket.blueprints
@tk.blanket.config_declarations
class DevelPlugin(p.IConfigurer, p.SingletonPlugin):
    @override
    def update_config(self, config: common.CKANConfig):

        tk.add_template_directory(config, "templates")
