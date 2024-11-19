"""Config getters of {{ cookiecutter.project_shortname }} plugin."""

from __future__ import annotations

import ckan.plugins.toolkit as tk

OPTION = "ckanext.{{ cookiecutter.project_shortname }}.option.name"
MULTI = "ckanext.{{ cookiecutter.project_shortname }}.multivalued.option"


def option() -> int:
    """Integer placerat tristique nisl."""
    return tk.config[OPTION]


def multivalued() -> list[str]:
    """Another option that will be parsed as a list of words."""
    return tk.config[MULTI]
