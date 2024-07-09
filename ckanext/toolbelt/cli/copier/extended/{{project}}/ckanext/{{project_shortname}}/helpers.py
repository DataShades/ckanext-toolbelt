"""Template helpers of the {{ project_shortname }} plugin.

All non-private functions defined here are registered inside `tk.h` collection.
"""

from __future__ import annotations


def {{project_shortname}}_hello() -> str:
    """Greet the user.

    Returns:
        greeting with the plugin name.
    """
    return "Hello, {{project_shortname}}!"
