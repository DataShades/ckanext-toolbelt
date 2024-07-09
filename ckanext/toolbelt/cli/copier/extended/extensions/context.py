from __future__ import annotations

from typing import Any

from copier_templates_extensions import ContextHook


class ContextUpdater(ContextHook):
    def hook(self, context: dict[str, Any]) -> dict[str, Any]:
        patch: dict[str, Any] = {}
        return patch
