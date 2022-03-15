from __future__ import annotations

from datetime import datetime
import logging

from typing import Any
from flask import Blueprint

import ckan.model as model
import ckan.plugins as p
import ckan.plugins.toolkit as tk
from ckan.views.group import group, organization, set_org, _replace_group_org

log = logging.getLogger(__name__)

toolbelt = Blueprint("toolbelt_group_changes", __name__)

CONFIG_WATCH_FIELDS = "ckanext.toolbelt.group_changes.watch_fields"
DEFAULT_WATCH_FIELDS = []


class GroupChangesPlugin(p.SingletonPlugin):
    p.implements(p.IConfigurer, inherit=True)
    p.implements(p.IBlueprint)
    p.implements(p.ITemplateHelpers)

    def get_helpers(self):
        return {
            "compare_group_dicts": compare_group_dicts,
        }

    def get_blueprint(self):
        return [toolbelt]

    def update_config(self, config):
        tk.add_template_directory(config, "templates/group_changes")


def check_metadata_org_changes(change_list, old, new):
    """
    Compares two versions of a organization and records the changes between
    them in change_list.
    """
    from ckan.lib.changes import _title_change

    # if the title has changed
    if old.get(u"title") != new.get(u"title"):
        _title_change(change_list, old, new)

    # if the description of the organization changed
    if old.get(u"description") != new.get(u"description"):
        _description_change(change_list, old, new)

    # if the image URL has changed
    if old.get(u"image_url") != new.get(u"image_url"):
        _image_url_change(change_list, old, new)

    watched = tk.aslist(
        tk.config.get(CONFIG_WATCH_FIELDS, DEFAULT_WATCH_FIELDS)
    )
    for field in watched:
        if old.get(field) != new.get(field):
            _custom_field_change(change_list, old, new, field)


def _custom_field_change(
    change_list: list[dict[str, Any]],
    old: dict[str, Any],
    new: dict[str, Any],
    field: str,
):
    """
    Appends a summary of a change to a organization's description between two
    versions (old and new) to change_list.
    """

    # if the old organization had a description
    if old.get(field) and new.get(field):
        change_list.append(
            {
                u"type": field,
                u"pkg_id": new.get(u"id"),
                u"title": new.get(u"title"),
                u"new_value": new.get(field),
                u"old_value": old.get(field),
                u"method": u"change",
            }
        )
    elif not new.get(field):
        change_list.append(
            {
                u"type": field,
                u"pkg_id": new.get(u"id"),
                u"title": new.get(u"title"),
                u"method": u"remove",
            }
        )
    else:
        change_list.append(
            {
                u"type": field,
                u"pkg_id": new.get(u"id"),
                u"title": new.get(u"title"),
                u"new_value": new.get(field),
                u"method": u"add",
            }
        )


def _description_change(change_list, old, new):
    """
    Appends a summary of a change to a organization's description between two
    versions (old and new) to change_list.
    """

    # if the old organization had a description
    if old.get(u"description") and new.get(u"description"):
        change_list.append(
            {
                u"type": u"description",
                u"pkg_id": new.get(u"id"),
                u"title": new.get(u"title"),
                u"new_description": new.get(u"description"),
                u"old_description": old.get(u"description"),
                u"method": u"change",
            }
        )
    elif not new.get(u"description"):
        change_list.append(
            {
                u"type": u"description",
                u"pkg_id": new.get(u"id"),
                u"title": new.get(u"title"),
                u"method": u"remove",
            }
        )
    else:
        change_list.append(
            {
                u"type": u"description",
                u"pkg_id": new.get(u"id"),
                u"title": new.get(u"title"),
                u"new_description": new.get(u"description"),
                u"method": u"add",
            }
        )


def _image_url_change(change_list, old, new):
    """
    Appends a summary of a change to a organization's image URL between two
    versions (old and new) to change_list.
    """
    # if both old and new versions have image  URLs
    if old.get(u"image_url") and new.get(u"image_url"):
        change_list.append(
            {
                u"type": u"image_url",
                u"method": u"change",
                u"pkg_id": new.get(u"id"),
                u"title": new.get(u"title"),
                u"new_image_url": new.get(u"image_url"),
                u"old_image_url": old.get(u"image_url"),
            }
        )
    # if the user removed the image URL
    elif not new.get(u"image_url"):
        change_list.append(
            {
                u"type": u"image_url",
                u"method": u"remove",
                u"pkg_id": new.get(u"id"),
                u"title": new.get(u"title"),
                u"old_image_url": old.get(u"image_url"),
            }
        )
    # if there wasn't one there before
    else:
        change_list.append(
            {
                u"type": u"image_url",
                u"method": u"add",
                u"pkg_id": new.get(u"id"),
                u"title": new.get(u"title"),
                u"new_image_url": new.get(u"image_url"),
            }
        )


def compare_group_dicts(
    old: dict[str, Any], new: dict[str, Any], old_activity_id: str
):
    """
    Takes two package dictionaries that represent consecutive versions of
    the same organization and returns a list of detailed & formatted summaries
    of the changes between the two versions. old and new are the two package
    dictionaries. The function assumes that both dictionaries will have
    all of the default package dictionary keys, and also checks for fields
    added by extensions and extra fields added by the user in the web
    interface.

    Returns a list of dictionaries, each of which corresponds to a change
    to the dataset made in this revision. The dictionaries each contain a
    string indicating the type of change made as well as other data necessary
    to form a detailed summary of the change.
    """
    change_list: list[dict[str, Any]] = []

    check_metadata_org_changes(change_list, old, new)

    # if the organization was updated but none of the fields we check
    # were changed, display a message stating that
    if len(change_list) == 0:
        change_list.append({u"type": "no_change"})

    return change_list


@toolbelt.route("/group/changes/<id>", endpoint="changes")
def changes(id: str) -> str:
    """
    Shows the changes to an organization in one particular activity stream
    item.
    """
    group_type = "group"
    set_org(False)
    extra_vars = {}
    activity_id = id
    context = {
        u"model": model,
        u"session": model.Session,
        u"user": tk.g.user,
        u"auth_user_obj": tk.g.userobj,
    }
    try:
        activity_diff = tk.get_action(u"activity_diff")(
            context,
            {
                u"id": activity_id,
                u"object_type": u"group",
                u"diff_type": u"html",
            },
        )
    except tk.ObjectNotFound as e:
        log.info(u"Activity not found: {} - {}".format(str(e), activity_id))
        return tk.abort(404, tk._(u"Activity not found"))
    except tk.NotAuthorized:
        return tk.abort(403, tk._(u"Unauthorized to view activity data"))

    # 'group_dict' needs to go to the templates for page title & breadcrumbs.
    # Use the current version of the package, in case the name/title have
    # changed, and we need a link to it which works
    group_id = activity_diff[u"activities"][1][u"data"][u"group"][u"id"]
    current_group_dict = tk.get_action(group_type + u"_show")(
        context, {u"id": group_id}
    )
    group_activity_list = tk.get_action(group_type + u"_activity_list")(
        context, {u"id": group_id, u"limit": 100}
    )

    extra_vars: dict[str, Any] = {
        u"activity_diffs": [activity_diff],
        u"group_dict": current_group_dict,
        u"group_activity_list": group_activity_list,
        u"group_type": current_group_dict[u"type"],
    }

    return tk.render(_replace_group_org(u"group/changes.html"), extra_vars)


@toolbelt.route("/group_type/changes_multiple", endpoint="changes_multiple")
def changes_multiple() -> str:
    """
    Called when a user specifies a range of versions they want to look at
    changes between. Verifies that the range is valid and finds the set of
    activity diffs for the changes in the given version range, then
    re-renders changes.html with the list.
    """
    group_type = "group"
    set_org(False)
    extra_vars = {}
    new_id = tk.h.get_request_param(u"new_id")
    old_id = tk.h.get_request_param(u"old_id")

    context = {
        u"model": model,
        u"session": model.Session,
        u"user": tk.g.user,
        u"auth_user_obj": tk.g.userobj,
    }

    # check to ensure that the old activity is actually older than
    # the new activity
    old_activity = tk.get_action(u"activity_show")(
        context, {u"id": old_id, u"include_data": False}
    )
    new_activity = tk.get_action(u"activity_show")(
        context, {u"id": new_id, u"include_data": False}
    )

    old_timestamp = old_activity[u"timestamp"]
    new_timestamp = new_activity[u"timestamp"]

    t1 = datetime.strptime(old_timestamp, u"%Y-%m-%dT%H:%M:%S.%f")
    t2 = datetime.strptime(new_timestamp, u"%Y-%m-%dT%H:%M:%S.%f")

    time_diff = t2 - t1
    # if the time difference is negative, just return the change that put us
    # at the more recent ID we were just looking at
    # TODO: do something better here - go back to the previous page,
    # display a warning that the user can't look at a sequence where
    # the newest item is older than the oldest one, etc
    if time_diff.total_seconds() < 0:
        return changes(tk.h.get_request_param(u"current_new_id"))

    done = False
    current_id = new_id
    diff_list = []

    while not done:
        try:
            activity_diff = tk.get_action(u"activity_diff")(
                context,
                {
                    u"id": current_id,
                    u"object_type": u"group",
                    u"diff_type": u"html",
                },
            )
        except tk.ObjectNotFound as e:
            log.info(u"Activity not found: {} - {}".format(str(e), current_id))
            return tk.abort(404, tk._(u"Activity not found"))
        except tk.NotAuthorized:
            return tk.abort(403, tk._(u"Unauthorized to view activity data"))

        diff_list.append(activity_diff)

        if activity_diff["activities"][0]["id"] == old_id:
            done = True
        else:
            current_id = activity_diff["activities"][0]["id"]

    group_id: str = diff_list[0][u"activities"][1][u"data"][u"group"][u"id"]
    current_group_dict = tk.get_action(group_type + u"_show")(
        context, {u"id": group_id}
    )
    group_activity_list = tk.get_action(group_type + u"_activity_list")(
        context, {u"id": group_id, u"limit": 100}
    )

    extra_vars: dict[str, Any] = {
        u"activity_diffs": diff_list,
        u"group_dict": current_group_dict,
        u"group_activity_list": group_activity_list,
        u"group_type": current_group_dict[u"type"],
    }

    return tk.render(_replace_group_org(u"group/changes.html"), extra_vars)
