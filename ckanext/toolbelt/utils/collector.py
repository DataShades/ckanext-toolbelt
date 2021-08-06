from __future__ import annotations

from typing import Any, Callable, TypeVar, Generic, Union

import copy

TFunc = TypeVar("TFunc", bound=Callable[..., Any])


class Collector(Generic[TFunc]):
    collection: dict[str, TFunc]

    def __init__(self, prefix="", separator="_"):
        self.collection = {}

        if prefix:
            self.prefix = prefix + separator
        else:
            self.prefix = ""

    def split(self) -> tuple[Collector, Callable[[], dict[str, TFunc]]]:
        return self, self.get_collection

    def __call__(self, func_or_name: Union[str, TFunc]):
        name: str

        def adder(func: TFunc):
            self.collection[name] = func
            return func

        if isinstance(func_or_name, str):
            name = func_or_name
            return adder

        name = self.prefix + getattr(func_or_name, "__name__")
        return adder(func_or_name)

    def get_collection(self) -> dict[str, TFunc]:
        return copy.copy(self.collection)
