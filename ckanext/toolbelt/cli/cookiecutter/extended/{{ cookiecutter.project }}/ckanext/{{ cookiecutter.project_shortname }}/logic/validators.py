from __future__ import annotations

from typing import Any

import ckan.plugins.toolkit as tk
from ckan import types


def {{ cookiecutter.project_shortname }}_required(value: Any):
    """Verify that value is not empty."""
    if not value or value is tk.missing:
        raise tk.Invalid("Required")

    return value


def {{ cookiecutter.project_shortname }}_complex_validator(
    key: types.FlattenKey,
    data: types.FlattenDataDict,
    errors: types.FlattenErrorDict,
    context: types.Context,
):
    """Verify that value is not empty."""
    if not data[key]:
        errors[key].append("Required")
        raise tk.StopOnError


def {{ cookiecutter.project_shortname }}_set_resource_url(
    key: types.FlattenKey,
    data: types.FlattenDataDict,
    errors: types.FlattenErrorDict,
    context: types.Context,
):
    """Move file_id into resource URL field as an external link."""
    url_key = key[:-1] + ("url",)
    type_key = key[:-1] + ("url_type",)

    data[url_key] = tk.url_for(
        "file.download",
        id=data[key],
        _external=True,
    )
    data[type_key] = "file"
