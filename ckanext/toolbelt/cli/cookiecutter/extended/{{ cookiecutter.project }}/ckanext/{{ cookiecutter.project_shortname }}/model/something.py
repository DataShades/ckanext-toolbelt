from __future__ import annotations

import copy
from typing import Any

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from ckan.lib.dictization import table_dictize
from ckan.model.meta import registry


@registry.mapped_as_dataclass
class Something:  # type: ignore
    """Model with details or something."""

    __tablename__ = "{{ cookiecutter.project_shortname }}_something"
    # define columns as a `__table__` attribute. It simplifies typing and you
    # can copy this definition almost unchanged into alembic migration.
    __table_args__ = ()

    id: Mapped[str] = mapped_column(primary_key=True, init=False)
    world: Mapped[str]
    hello: Mapped[str] = mapped_column(default="")
    plugin_data: Mapped[dict[str, Any]] = mapped_column(JSONB, default_factory=dict)

    def dictize(self, context: Any) -> dict[str, Any]:
        """Transform model into dictionary."""
        result = table_dictize(self, context)

        plugin_data = result.pop("plugin_data")
        if context.get("include_plugin_data"):
            result["plugin_data"] = copy.deepcopy(plugin_data)

        return result

    @classmethod
    def by_hello(cls, hello: str, world: str | None = None):
        """Filter objects by the value of hello column."""
        stmt = sa.select(cls).where(
            cls.hello == hello,
        )

        if world:
            stmt = stmt.where(cls.world == world)

        return stmt
