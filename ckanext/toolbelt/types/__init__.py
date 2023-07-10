from __future__ import annotations

from typing_extensions import NotRequired, TypedDict


class SelectOption(TypedDict):
    text: NotRequired[str]
    value: str
