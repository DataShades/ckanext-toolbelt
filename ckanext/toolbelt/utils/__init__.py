from __future__ import annotations

from typing import Any, Callable, TypeVar

import ckan.plugins.toolkit as tk

T = TypeVar("T")

__all__ = [
    "constantly",
    "config_getter",
]


def constantly(v: T) -> Callable[..., T]:
    return lambda *args, **kwargs: v


def config_getter(
    name: str,
    default: T | str | None,
    convert: Callable[[T | str | None], T] | None = None,
) -> Callable[..., T | str | None]:
    def getter(*_args: Any, **_kwargs: Any):
        v = tk.config.get(name, default)
        if convert:
            v = convert(v)
        return v

    return getter
