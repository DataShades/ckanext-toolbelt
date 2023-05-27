from __future__ import annotations

import dataclasses
from typing import TYPE_CHECKING, Any, Generic, TypeVar

if TYPE_CHECKING:
    from collections.abc import Collection


T = TypeVar("T")


@dataclasses.dataclass
class Node(Generic[T]):
    value: T
    leaves: Collection[Node[T]] = ()
    parent: Node[T] | None = None
    data: dict[str, Any] = dataclasses.field(default_factory=dict)

    def __iter__(self):
        return iter(self.leaves)

    def __len__(self):
        return len(self.leaves)

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Node):
            return False

        return bool(self.value == other.value and self.leaves == other.leaves)
