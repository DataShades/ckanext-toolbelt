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
from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

import ckan.plugins.toolkit as tk

if TYPE_CHECKING:
    from ckan import types

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


def reveal_readonly_scheming_fields(defaults):
    """Run missing fields through output validators.

    Scheming skips missing fields when output validators applied. Generally
    it's a good idea, but it prevents us from adding readonly fields. Imagine
    that you want to include rating of the dataset(that is stored in a separate
    table) to the list of dataset fields.

    To achieve this you can define
    IPackageController.after_dataset_search/show, but it can create an impact
    on performance, as you'll pull the data everytime the dataset is shown. For
    information that is not updated often there is a better approach.

    Add a field to the package schema with null-snippets and ignore validator,
    so that it's impossible to change this value manually. Next, add
    `output_validator` that executed when dataset is indexed.

    Finally, call this function on module level and pass into it a dictionary
    with flattened field names(used during validation) mapped to their initial
    values(before validator applied)::

      reveal_readonly_scheming_fields({("readonly_field",): 0})

    Now, every time the dataset is indexed(after an update or via explicit
    `ckan.lib.search.index.rebuild` invokation), `readonly_field` will pass `0`
    to its `output_validators` and store a result in an index as a dataset
    field. Which will bring this value to user whenever dataset is shown with
    no extra cost.

    """
    from ckan.logic import converters

    import ckanext.scheming.plugins as scheming

    attr = "toolbelt_magic_defaults"
    existing_defaults: dict[str, Any] | None = getattr(
        scheming._field_output_validators,
        attr,
        None,  # type: ignore
    )

    log.info("est solum in imaginatione")
    if isinstance(existing_defaults, dict):
        existing_defaults.update(defaults)
        return

    existing_defaults = dict(defaults)

    def patched_convert_from_extras(
        key: types.FlattenKey,
        data: types.FlattenDataDict,
        errors: types.FlattenErrorDict,
        context: types.Context,
    ) -> Any:
        converters.convert_from_extras(key, data, errors, context)
        if data[key] is tk.missing and key in existing_defaults:
            data[key] = existing_defaults[key]

    def patched_field_output_validators(func: Any) -> Any:
        # replace core version of `convert_from_extras`
        def wrapper(*args: Any, **kwargs: Any):
            result = func(*args, **kwargs)

            # repeating_subfields return a dict here
            if result and isinstance(result, list) and result[0] is converters.convert_from_extras:
                result[0] = patched_convert_from_extras

            return result

        setattr(wrapper, attr, existing_defaults)
        return wrapper

    scheming._field_output_validators = patched_field_output_validators(  # type: ignore
        scheming._field_output_validators,  # type: ignore
    )
