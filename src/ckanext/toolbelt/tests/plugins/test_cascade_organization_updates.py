from unittest import mock

import pytest

import ckan.plugins.toolkit as tk
from ckan.lib import jobs
from ckan.tests.helpers import RQTestBase, call_action

from ckanext.toolbelt.plugins.cascade_organization_updates import reindex_organization


@pytest.mark.usefixtures("clean_db", "clean_index")
@pytest.mark.ckan_config("ckan.plugins", "toolbelt_cascade_organization_updates")
@pytest.mark.usefixtures("with_plugins")
class TestFlow(RQTestBase):
    def test_basic(self, organization, package_factory):
        pkg = package_factory(owner_org=organization["id"])

        call_action("organization_update", **dict(organization, title="Updated"))

        updated_pkg = call_action("package_show", id=pkg["id"])
        assert updated_pkg["organization"]["title"] != "Updated"

        jobs.Worker().work(True)

        updated_pkg = call_action("package_show", id=pkg["id"])
        assert updated_pkg["organization"]["title"] == "Updated"


@pytest.mark.usefixtures("clean_db")
@pytest.mark.ckan_config("ckan.plugins", "toolbelt_cascade_organization_updates")
@pytest.mark.usefixtures("with_plugins")
class TestEnqueue:
    @mock.patch("ckan.plugins.toolkit.enqueue_job")
    def test_enqueued_with_org_id(self, stub, organization):
        stub.assert_not_called()
        call_action("organization_update", **dict(organization, title="Updated"))

        stub.assert_called_once_with(reindex_organization, [organization["id"]])

    @mock.patch("ckan.plugins.toolkit.enqueue_job")
    def test_not_enqueued_for_missing_organization(self, stub):
        with pytest.raises(tk.ObjectNotFound):
            call_action("organization_update", id="not real")

        stub.assert_not_called()


@pytest.mark.usefixtures("clean_db", "clean_index")
@pytest.mark.ckan_config("ckan.plugins", "toolbelt_cascade_organization_updates")
@pytest.mark.usefixtures("with_plugins")
class TestJob:
    def test_basic(self, organization, package_factory):
        names = ["first", "second"]
        for name in names:
            pkg = package_factory(owner_org=organization["id"], name=name)

        call_action("organization_update", **dict(organization, title="Updated"))

        for name in names:
            pkg = call_action("package_show", id=name)
            assert pkg["organization"]["title"] != "Updated"

        reindex_organization("not-real")

        for name in names:
            pkg = call_action("package_show", id=name)
            assert pkg["organization"]["title"] != "Updated"

        reindex_organization(organization["id"])

        for name in names:
            pkg = call_action("package_show", id=name)
            assert pkg["organization"]["title"] == "Updated"
