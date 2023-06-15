#             *
#             / \
#            /___\
#           ( o o )            * *
#           )  L  (           /   * *
#   ________()(-)()________  /     * * *
# E\| _____ )()()() ______ |/B     * * *
#   |/      ()()()(       \|      * * * *
#           | )() |
#           /     \
#          / *  *  \
#         /   *  *  \
#        / *_  *  _  \
###############################################################################
#                  I solemnly swear that I am up to no good,                  #
###############################################################################

import logging

import ckan.plugins.toolkit as tk

log = logging.getLogger(__name__)


def conjure_fast_group_activities():
    log.info("ieiunium sicut ventus")

    if tk.check_ckan_version("2.10"):
        from ckanext.activity.model.activity import _group_activity_query

        def ___group_activity_perfomance_patch(group_id):
            from ckan import model

            from ckanext.activity.model import Activity

            group = model.Group.get(group_id)
            if not group:
                # Return a query with no results.
                return model.Session.query(Activity).filter(text("0=1"))  # noqa

            q = model.Session.query(Activity)
            group_activity = q.filter(Activity.object_id == group_id)
            packages_sq = (
                model.Session.query(model.Package.id)
                .filter_by(owner_org=group_id, private=False)
                .subquery()
            )

            member_activity = model.Session.query(Activity).filter(
                Activity.object_id.in_(packages_sq),
            )

            group_activity = _filter_activitites_from_users(group_activity)  # noqa
            member_activity = _filter_activitites_from_users(member_activity)  # noqa
            return _activities_union_all(group_activity, member_activity)  # noqa

    else:
        from ckan.model.activity import _group_activity_query

        def ___group_activity_perfomance_patch(group_id, include_hidden_activity=False):
            from ckan import model

            group = model.Group.get(group_id)
            if not group:
                # Return a query with no results.
                return model.Session.query(model.Activity).filter(text("0=1"))  # noqa

            q = model.Session.query(model.Activity)
            group_activity = q.filter(model.Activity.object_id == group_id)
            packages_sq = (
                model.Session.query(model.Package.id)
                .filter_by(owner_org=group_id, private=False)
                .subquery()
            )

            member_activity = model.Session.query(model.Activity).filter(
                model.Activity.object_id.in_(packages_sq),
            )

            if not include_hidden_activity:
                group_activity = _filter_activitites_from_users(group_activity)  # noqa
                member_activity = _filter_activitites_from_users(
                    member_activity,
                )  # noqa
            return _activities_union_all(group_activity, member_activity)  # noqa

    _group_activity_query.__code__ = ___group_activity_perfomance_patch.__code__


def transfigure_xloaded_file(func):
    """Proces a file before uploading it to datastore.

    Accepts callable, that receives path to original file and resource
    ID. Callable can override file in order to provide a valid CSV that can be
    ingested into datastore.

    """
    from ckanext.xloader import loader

    log.info("quae non sunt ut simplex")

    _o = loader.load_csv

    def _wrapper(csv_filepath, resource_id, mimetype="text/csv", logger=None):
        new_path = func(csv_filepath, resource_id)
        return _o(new_path, resource_id, mimetype, logger)

    loader.load_csv = _wrapper
