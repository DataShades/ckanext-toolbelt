from typing import Callable, TypeVar


T = TypeVar("T")


def constantly(v: T) -> Callable[..., T]:
    return lambda *args, **kwargs: v
