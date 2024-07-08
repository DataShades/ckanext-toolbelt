from __future__ import annotations

from ckan import types
from ckan.logic.schema import validator_args


@validator_args
def get_sum(
    convert_int: types.Validator,
    not_empty: types.Validator,
) -> types.Schema:
    """Schema for {{ project_shortname }}_get_sum action."""
    return {
        "left": [not_empty, convert_int],
        "right": [not_empty, convert_int],
    }
