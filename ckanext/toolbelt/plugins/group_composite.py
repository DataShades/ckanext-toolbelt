import ckan.plugins.toolkit as tk

from ckanext.scheming.plugins import (
    SchemingOrganizationsPlugin,
    SchemingGroupsPlugin,
    _field_output_validators_group,
    _field_create_validators,
    _field_validators,
    validation,
    unflatten,
    convert_to_extras,
    json,
    expand_form_composite,
)


class CompositeMixin:
    def validate(self, context, data_dict, schema, action):
        """
        Validate and convert for package_create, package_update and
        package_show actions.
        """
        thing, action_type = action.split("_")
        t = data_dict.get("type")
        if not t or t not in self._schemas:
            return data_dict, {
                "type": "Unsupported {thing} type: {t}".format(
                    thing=thing, t=t
                )
            }

        scheming_schema = self._expanded_schemas[t]

        before = scheming_schema.get("before_validators")
        after = scheming_schema.get("after_validators")
        if action_type == "show":
            get_validators = _field_output_validators_group
            before = after = None
        elif action_type == "create":
            get_validators = _field_create_validators
        else:
            get_validators = _field_validators

        if before:
            schema["__before"] = validation.validators_from_string(
                before, None, scheming_schema
            )
        if after:
            schema["__after"] = validation.validators_from_string(
                after, None, scheming_schema
            )
        fg = ((scheming_schema["fields"], schema, True),)

        composite_convert_fields = []
        for field_list, destination, convert_extras in fg:
            for f in field_list:
                convert_this = convert_extras and f["field_name"] not in schema
                destination[f["field_name"]] = get_validators(
                    f, scheming_schema, convert_this
                )
                if convert_this and "repeating_subfields" in f:
                    composite_convert_fields.append(f["field_name"])

        def composite_convert_to(key, data, errors, context):
            unflat = unflatten(data)
            for f in composite_convert_fields:
                if f not in unflat:
                    continue
                data[(f,)] = json.dumps(
                    unflat[f], default=lambda x: None if x == tk.missing else x
                )
                convert_to_extras((f,), data, errors, context)
                del data[(f,)]

        if action_type == "show":
            if composite_convert_fields:
                for ex in data_dict["extras"]:
                    if ex["key"] in composite_convert_fields:
                        try:
                            value = json.loads(ex["value"])
                        except (ValueError, TypeError):
                            value = []
                        data_dict[ex["key"]] = value
                data_dict["extras"] = [
                    ex
                    for ex in data_dict["extras"]
                    if ex["key"] not in composite_convert_fields
                ]
        else:
            group_composite = {
                f["field_name"]
                for f in scheming_schema["fields"]
                if "repeating_subfields" in f
            }
            if group_composite:
                expand_form_composite(data_dict, group_composite)
            # convert composite package fields to extras so they are stored
            if composite_convert_fields:
                schema = dict(
                    schema,
                    __after=schema.get("__after", []) + [composite_convert_to],
                )

        for f in composite_convert_fields:
            if not isinstance(data_dict.get(f), str):
                continue
            try:
                data_dict[f] = json.loads(data_dict[f])
            except ValueError:
                pass

        return tk.navl_validate(data_dict, schema, context)


class CompositeGroupsPlugin(CompositeMixin, SchemingGroupsPlugin):
    pass

class CompositeOrganizationsPlugin(CompositeMixin, SchemingOrganizationsPlugin):
    pass
