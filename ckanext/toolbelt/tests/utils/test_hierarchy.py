import pytest

import ckan.plugins.toolkit as tk

import ckanext.toolbelt.utils.hierarchy as h

PARENT_FIELD = "notes"


@pytest.mark.ckan_config(h.CONFIG_CHILD_DISTANCE, 5)
@pytest.mark.ckan_config(h.CONFIG_PARENT_DISTANCE, 5)
@pytest.mark.ckan_config(h.CONFIG_PARENT_FIELD, PARENT_FIELD)
@pytest.mark.usefixtures(
    "with_plugins",
    "clean_db",
    "clean_index",
    "with_request_context",
)
class TestPackageHierarchy:
    def test_missing_package(self):
        with pytest.raises(tk.ObjectNotFound):
            h.package_hierarchy("not a real package")

    def test_orphan(self, package, user_factory):
        sysadmin = user_factory(sysadmin=True)
        node = h.package_hierarchy(package["id"], {"user": sysadmin["name"]})

        assert not node
        assert node.value["name"] == package["name"]

    def test_equality(self, package_factory, user_factory):
        sysadmin = user_factory(sysadmin=True)

        parent = package_factory()
        brother = package_factory(**{PARENT_FIELD: parent["id"]})
        sister = package_factory(**{PARENT_FIELD: parent["id"]})

        parent_hierarchy = h.package_hierarchy(parent["id"], {"user": sysadmin["name"]})
        brother_hierarchy = h.package_hierarchy(
            brother["id"],
            {"user": sysadmin["name"]},
        )
        sister_hierarchy = h.package_hierarchy(sister["id"], {"user": sysadmin["name"]})

        assert parent_hierarchy == brother_hierarchy == sister_hierarchy

    def test_family(self, package_factory, user_factory):
        sysadmin = user_factory(sysadmin=True)

        grand_parent = package_factory()
        parent = package_factory(**{PARENT_FIELD: grand_parent["id"]})

        brother = package_factory(**{PARENT_FIELD: parent["id"]})
        brother_child = package_factory(**{PARENT_FIELD: brother["id"]})

        sister = package_factory(**{PARENT_FIELD: parent["id"]})
        sister_child = package_factory(**{PARENT_FIELD: sister["id"]})

        hierarchy = h.package_hierarchy(parent["id"], {"user": sysadmin["name"]})

        assert hierarchy.value["id"] == grand_parent["id"]
        assert len(hierarchy) == 1

        ph = next(iter(hierarchy.leaves))
        assert ph.value["id"] == parent["id"]
        assert len(ph) == 2

        siblings_iter = iter(ph.leaves)

        # sister comes first because of default sorting by newest metadata
        # creation
        sh = next(siblings_iter)
        assert sh.value["id"] == sister["id"]
        assert len(sh) == 1

        sch = next(iter(sh.leaves))
        assert sch.value["id"] == sister_child["id"]
        assert len(sch) == 0

        bh = next(siblings_iter)
        assert bh.value["id"] == brother["id"]
        assert len(bh) == 1

        bch = next(iter(bh.leaves))
        assert bch.value["id"] == brother_child["id"]
        assert len(bch) == 0
