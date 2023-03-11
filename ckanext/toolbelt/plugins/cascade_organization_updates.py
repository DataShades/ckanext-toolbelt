from __future__ import annotations

import logging

import ckan.plugins as p
import ckan.plugins.toolkit as tk
from ckan import model
from ckan.lib.search import commit, rebuild

log = logging.getLogger(__name__)


class CascadeOrganizationUpdatesPlugin(p.SingletonPlugin):
    p.implements(p.IActions)

    def get_actions(self):
        return {
            "organization_update": organization_update,
        }


@tk.chained_action
def organization_update(next_, context, data_dict):
    """Reindex all datasets inside the organization after any update."""
    result = next_(context, data_dict)
    tk.enqueue_job(reindex_organization, [result["id"]])
    return result


def reindex_organization(id_or_name: str):
    """Rebuild search index for all datasets inside the organization."""
    org = model.Group.get(id_or_name)

    if not org:
        log.warning("Organization with ID or name %s not found", id_or_name)
        return

    query = model.Session.query(model.Package.id).filter_by(owner_org=org.id)

    rebuild(package_ids=(p.id for p in query), force=True)
    commit()
