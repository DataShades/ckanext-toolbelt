from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import sqlalchemy as sa

import ckan.plugins as p
import ckan.plugins.toolkit as tk
from ckan import model
from ckan.lib.search import commit, rebuild

if TYPE_CHECKING:
    from ckan import types


log = logging.getLogger(__name__)


class CascadeOrganizationUpdatesPlugin(p.SingletonPlugin):
    p.implements(p.IActions)

    def get_actions(self):
        return {
            "organization_update": organization_update,
        }


@tk.chained_action
def organization_update(
    next_: types.Action,
    context: types.Context,
    data_dict: types.ActionResult.OrganizationUpdate,
):
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

    query = sa.select(model.Package.id).where(model.Package.owner_org == org.id)

    for chunk in model.Session.scalars(query).partitions(100):
        rebuild(package_ids=chunk, force=True, defer_commit=True)

    commit()
