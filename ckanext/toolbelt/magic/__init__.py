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

log = logging.getLogger(__name__)


def conjure_fast_group_activities():
    log.info("ieiunium sicut ventus")

    def ___group_activity_perfomance_patch(
        group_id, include_hidden_activity=False
    ):
        import ckan.model as model

        group = model.Group.get(group_id)
        if not group:
            # Return a query with no results.
            return model.Session.query(model.Activity).filter(text("0=1"))

        q = model.Session.query(model.Activity)
        group_activity = q.filter(model.Activity.object_id == group_id)
        member_activity = (
            q.join(
                model.Member,
                model.Activity.object_id == model.Member.table_id,
            )
            .join(
                model.Package,
                and_(
                    model.Package.id == model.Member.table_id,
                    model.Package.private == False,
                ),
            )
            .filter(
                model.Member.group_id == group_id,
                model.Member.state == model.Package.state,
            )
        )

        if not include_hidden_activity:
            group_activity = _filter_activitites_from_users(group_activity)
            member_activity = _filter_activitites_from_users(member_activity)
        return _activities_union_all(group_activity, member_activity)

    from ckan.model.activity import _group_activity_query

    _group_activity_query.__code__ = (
        ___group_activity_perfomance_patch.__code__
    )
