from __future__ import annotations

from typing import Callable, Optional, TypeVar, Union
import ckan.plugins.toolkit as tk


T = TypeVar("T")

__all__ = [
    "constantly", "config_getter",
]

def constantly(v: T) -> Callable[..., T]:
    return lambda *args, **kwargs: v


def config_getter(
        name: str,
        default: Union[T, str, None],
        convert: Optional[Callable[[Union[T, str, None]], T]] = None
) -> Callable[..., Union[T, str, None]]:
    def getter(*args, **kwargs):
        v = tk.config.get(name, default)
        if convert:
            v = convert(v)
        return v

    return getter
