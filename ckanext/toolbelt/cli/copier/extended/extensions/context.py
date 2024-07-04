from __future__ import annotations

from copier import Any
from copier_templates_extensions import ContextHook


class ContextUpdater(ContextHook):
    def hook(self, context: dict[str, Any]) -> dict[str, Any]:
        patch: dict[str, Any] = {}
        return patch
        # flavor = context["flavor"]  # user's answer to the "flavor" question
        # return {
        #     "isDocker": flavor == "docker"
        #     "isK8s": flavor == "kubernetes"
        #     "isInstances": flavor == "instances"
        #     "isLite": flavor == "none"
        #     "isNotDocker": flavor != "docker"
        #     "isNotK8s": flavor != "kubernetes"
        #     "isNotInstances": flavor != "instances"
        #     "isNotLite": flavor != "none"
        #     "hasContainers": flavor in {"docker", "kubernetes"}
        # }
