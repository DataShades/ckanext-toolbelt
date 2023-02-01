from __future__ import annotations

import dataclasses
from typing import Any, Generic, Optional, TypeVar
from collections.abc import Collection

T = TypeVar("T")


@dataclasses.dataclass
class Node(Generic[T]):
    value: T
    leaves: Collection[Node[T]] = ()
    parent: Optional[Node] = None
    data: dict[str, Any] = dataclasses.field(default_factory=dict)

    def __iter__(self):
        return iter(self.leaves)

    def __len__(self):
        return len(self.leaves)

    def __eq__(self, other: Any):
        if not isinstance(other, Node):
            return False

        return self.value == other.value and self.leaves == other.leaves
