from __future__ import annotations

import abc
import logging
from typing import TYPE_CHECKING, Any, Iterable

import ckan.plugins.toolkit as tk
from ckan.lib.search.query import solr_literal

from ckanext.toolbelt.utils.structures import Node

if TYPE_CHECKING:
    from typing_extensions import TypeAlias

log = logging.getLogger(__name__)

PackageDict: TypeAlias = "dict[str, Any]"

CONFIG_PARENT_FIELD = "ckanext.toolbelt.package_hierarchy.parent_field"
DEFAULT_PARENT_FIELD = "parent_id"

CONFIG_REFERENCE_FIELD = "ckanext.toolbelt.package_hierarchy.reference_field"
DEFAULT_REFERENCE_FIELD = "id"

CONFIG_PARENT_DISTANCE = "ckanext.toolbelt.package_hierarchy.parent_distance"
DEFAULT_PARENT_DISTANCE = 10

CONFIG_CHILD_DISTANCE = "ckanext.toolbelt.package_hierarchy.child_distance"
DEFAULT_CHILD_DISTANCE = 10

CONFIG_SIBLING_LIMIT = "ckanext.toolbelt.package_hierarchy.sibling_limit"
DEFAULT_SIBLING_LIMIT = 20


def config_parent_field() -> str:
    return tk.config.get(CONFIG_PARENT_FIELD, DEFAULT_PARENT_FIELD)


def config_reference_field() -> str:
    return tk.config.get(CONFIG_REFERENCE_FIELD, DEFAULT_REFERENCE_FIELD)


def config_parent_distance() -> int:
    return tk.asint(tk.config.get(CONFIG_PARENT_DISTANCE, DEFAULT_PARENT_DISTANCE))


def config_child_distance() -> int:
    return tk.asint(tk.config.get(CONFIG_CHILD_DISTANCE, DEFAULT_CHILD_DISTANCE))


def config_sibling_limit() -> int:
    return tk.asint(tk.config.get(CONFIG_SIBLING_LIMIT, DEFAULT_SIBLING_LIMIT))


class Strategy(abc.ABC):
    def __init__(self, context: dict[str, Any]):
        self.context = context

        parent_distance = config_parent_distance()
        child_distance = config_child_distance()
        sibling_limit = config_sibling_limit()

        if tk.request:
            parent_distance = tk.asint(
                tk.request.args.get("__relationship_parent_distance", parent_distance),
            )
            child_distance = tk.asint(
                tk.request.args.get("__relationship_child_distance", child_distance),
            )

            sibling_limit = tk.asint(
                tk.request.args.get("__relationship_sibling_limit", sibling_limit),
            )

        self.parent_distance = parent_distance
        self.child_distance = child_distance
        self.sibling_limit = sibling_limit

    @abc.abstractmethod
    def root(self, pkg: PackageDict) -> tuple[PackageDict, int]:
        raise NotImplementedError

    @abc.abstractmethod
    def children(self, pkg: PackageDict) -> Iterable[PackageDict]:
        raise NotImplementedError


class ParentReference(Strategy):
    def __init__(self, context: dict[str, Any]):
        super().__init__(context)
        self.parent_field = config_parent_field()
        self.reference_field = config_reference_field()

    def root(self, pkg: PackageDict) -> tuple[PackageDict, int]:
        root: PackageDict = pkg
        i = 0
        while i < self.parent_distance:
            if not root.get(self.parent_field):
                break

            key = self.reference_field
            value = solr_literal(root[self.parent_field])
            results = tk.get_action("package_search")(
                dict(self.context),
                {"q": f"{key}:{value}"},
            )["results"]
            if not results:
                break

            if len(results) > 1:
                log.warning(
                    "Multiple packages found by %s with value %s",
                    self.reference_field,
                    root[self.parent_field],
                )
            root = results[0]

            i += 1

        return root, i

    def children(self, pkg: PackageDict):
        key = self.parent_field
        value = pkg[self.reference_field]
        return tk.get_action("package_search")(
            {},
            {
                "fq": f"{key}:({value})",
                "rows": self.sibling_limit,
            },
        )["results"]


def package_hierarchy(
    id_: str,
    context: dict[str, Any] | None = None,
    strategy_factory: type[Strategy] = ParentReference,
) -> Node[PackageDict]:
    """Return a Node starting from the **reacheable** root of the package's
    hierarchy.
    """
    ctx = context or {}
    root: PackageDict = tk.get_action("package_show")(dict(ctx), {"id": id_})

    strategy = strategy_factory(ctx)
    root, distance = strategy.root(root)

    return _package_as_node(root, distance, strategy)


def _package_as_node(
    pkg: PackageDict,
    buffer: int,
    strategy: Strategy,
) -> Node[PackageDict]:
    """Recursive function that wraps package into Node and attach children to
    it as leaves.

    """
    children: Iterable[PackageDict]

    depth_capacity = buffer + strategy.child_distance
    children = strategy.children(pkg) if depth_capacity else []

    node = Node(
        pkg,
        [_package_as_node(child, buffer - 1, strategy) for child in children],
    )

    for child in node.leaves:
        child.parent = node

    return node
