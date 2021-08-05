from __future__ import annotations

from typing import Any, Callable, TypeVar, Generic, Union

import copy

T = TypeVar("T", bound=Callable[..., Any])


class Collector(Generic[T]):
    collection: dict[str, T]

    def __init__(self, prefix="", separator="_"):
        self.collection = {}

        if prefix:
            self.prefix = prefix + separator
        else:
            self.prefix = ""

    def split(self) -> tuple[Collector, Callable[[], dict[str, T]]]:
        return self, self.get_collection


    def __call__(self, func_or_name: Union[str, T]):
        name: str
        def adder(func: T):
            self.collection[name] = func
            return func

        if isinstance(func_or_name, str):
            name = func_or_name
            return adder

        name = self.prefix + getattr(func_or_name, "__name__")
        return adder(func_or_name)


    def get_collection(self) -> dict[str, T]:
        return copy.copy(self.collection)
