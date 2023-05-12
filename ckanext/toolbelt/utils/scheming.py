from __future__ import annotations

import logging
from difflib import get_close_matches
from typing import TYPE_CHECKING, Literal

import ckan.plugins.toolkit as tk

if TYPE_CHECKING:
    from ckan.types import Schema

log = logging.getLogger(__name__)

_field_sources = {
    "organization": "fields",
    "group": "fields",
    "dataset": "dataset_fields",
    "resource": "resource_fields",
}


def get_validation_schema(
    entity: Literal["dataset", "resource", "organization", "group"],
    type_: str,
    fields_source: str | None = None,
) -> Schema | None:
    """Convert entity schema from scheming into validation schema."""
    from ckanext.scheming.plugins import _field_create_validators

    try:
        schema = tk.get_action(f"scheming_{entity}_schema_show")(
            {"ignore_auth": True},
            {"type": type_},
        )

    except tk.ObjectNotFound:
        types: list[str] = tk.get_action(f"scheming_{entity}_schema_list")(
            {"ignore_auth": True},
            {},
        )
        similar = get_close_matches(type_, types, 1)
        if similar:
            log.warning(
                "Cannot locate %s schema for %s. Did you mean %s?",
                entity,
                type_,
                similar[0],
            )
        else:
            log.warning(
                "Cannot locate %s schema for %s.",
                entity,
                type_,
            )
        return None

    except KeyError:
        log.warning(
            "Cannot locate any %s schemas. Is scheming plugin for this entity enabled?",
            entity,
        )
        return None

    if not fields_source:
        fields_source = _field_sources[entity]

    return {
        f["field_name"]: _field_create_validators(f, schema, False)
        for f in schema[fields_source]
    }
