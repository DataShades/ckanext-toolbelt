from __future__ import annotations

from typing import Any

import ckan.plugins as p
from ckan import types


class PackageController(p.SingletonPlugin):
    """Customize dataset lifecycle."""

    p.implements(p.IPackageController, inherit=True)

    def after_dataset_show(
        self,
        context: types.Context,
        pkg_dict: dict[str, Any],
    ) -> None:
        """Hide private data."""

    def before_dataset_search(self, search_params: dict[str, Any]) -> dict[str, Any]:
        """Improve search filters."""
        return search_params
