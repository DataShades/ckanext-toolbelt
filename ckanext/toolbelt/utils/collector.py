from __future__ import annotations

import copy
from typing import TYPE_CHECKING, Any, Callable, Generic, TypeVar

if TYPE_CHECKING:
    from typing_extensions import Self

TFunc = TypeVar("TFunc", bound=Callable[..., Any])


class Collector(Generic[TFunc]):
    collection: dict[str, TFunc]

    def __init__(self, prefix: str = "", separator: str = "_"):
        self.collection = {}

        if prefix:
            self.prefix = prefix + separator

        else:
            self.prefix = ""

    def split(self) -> tuple[Self, Callable[[], dict[str, TFunc]]]:
        return self, self.get_collection

    def __call__(self, func_or_name: str | TFunc):
        name: str

        def adder(func: TFunc):
            self.collection[name] = func
            return func

        if isinstance(func_or_name, str):
            name = func_or_name
            return adder

        name = self.prefix + func_or_name.__name__
        return adder(func_or_name)

    def get_collection(self) -> dict[str, TFunc]:
        return copy.copy(self.collection)
