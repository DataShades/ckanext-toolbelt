"""Template helpers of the {{ cookiecutter.project_shortname }} plugin.

All non-private functions defined here are registered inside `tk.h` collection.
"""

from __future__ import annotations


def {{ cookiecutter.project_shortname }}_hello() -> str:
    """Greet the user.

    Returns:
        greeting with the plugin name.
    """
    return "Hello, {{ cookiecutter.project_shortname }}!"
