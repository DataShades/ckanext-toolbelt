from __future__ import annotations

from typing import Any

import pytest
from faker import Faker
from playwright.sync_api import Page, expect

from ckan import types
from ckan.tests.helpers import call_action  # pyright: ignore[reportUnknownVariableType]

from ckanext.toolbelt.tests.e2e_base._locators import ElementLocator

__all__ = [
    "Login",
    "Logout",
    "Profile",
    "StandardUser",
]


class Login(ElementLocator):
    @pytest.mark.ckan_standard("login")
    def test_login_normal(self, page: Page, user_factory: types.TestFactory, faker: Faker, milestone_screenshot: Any):
        """Test normal login flow.

        Given an existing user
        When they go to the login page
        And fill in their username and password
        And submit the form
        Then they are redirected to the dashboard
        And their display name is shown in the header
        """
        password = faker.password()
        user = user_factory(password=password)

        page.goto("/")

        self.locate_login_link(page).click()
        expect(page).to_have_url("/user/login")

        page.get_by_label("username").fill(user["name"])
        page.get_by_label("password").fill(password)

        milestone_screenshot("form_with_credentials")

        self.locate_login_button(page).click()
        expect(page).to_have_url("/dashboard/datasets")

        profile_link = self.locate_profile_link(page, user)
        expect(profile_link).to_be_visible()

        milestone_screenshot("after_login_redirect")

    @pytest.mark.ckan_standard("login")
    def test_login_authenticated(self, milestone_screenshot: Any, login: Any, user: dict[str, Any], page: Page):
        """Authenticated user cannot access login page again.

        Given an authenticated user
        When they go to the login page
        Then they see a message that they are already logged in
        And the username and password fields are disabled
        """
        login(user["name"])

        page.goto("/user/login")
        expect(self.locate_login_link(page)).not_to_be_attached()

        expect(self.locate_existing_login_session_alert(page)).to_be_visible()
        milestone_screenshot("existing_session_alert")


class Logout(ElementLocator):
    @pytest.mark.ckan_standard("logout")
    def test_logout_normal(self, milestone_screenshot: Any, user: dict[str, Any], page: Page, login: Any):
        """Test normal logout flow.

        Given an authenticated user
        When they click the logout link
        Then they are redirected to the post-logout page
        And they see a message that they have been logged out
        And the login link is visible in the header
        """
        login(user)
        page.goto("/")
        self.locate_logout_link(page).click()

        expect(page).to_have_url("/user/logged_out_redirect")
        expect(self.locate_logged_out_alert(page)).to_be_visible()

        expect(self.locate_login_link(page)).to_be_visible()
        expect(self.locate_logout_link(page)).not_to_be_attached()
        milestone_screenshot("post_logout_redirect")

    @pytest.mark.ckan_standard("logout")
    def test_logout_anonymous(self, milestone_screenshot: Any, page: Page):
        """Test anonymous user logout flow.

        Given an anonymous user
        When they go to the logout page
        Then they are redirected to the login page
        """
        page.goto("/user/_logout")
        expect(page).to_have_url("/user/login")
        milestone_screenshot("redirect_to_login")


class Profile(ElementLocator):
    @pytest.mark.ckan_standard("profile")
    def test_profile_tabs(self, milestone_screenshot: Any, login: Any, page: Page, user: dict[str, Any]):
        """Test navigation between profile tabs.

        Given an authenticated user
        When they go to their profile page
        Then they can navigate between the Datasets, Organizations, Groups, and API Tokens tabs
        And the URL updates accordingly
        """
        login(user["name"])

        page.goto("/")
        self.locate_profile_link(page, user).click()
        milestone_screenshot("main_page")

        self.locate_profile_datasets_tab(page).click()
        expect(page).to_have_url(f"/user/{user['name']}")
        milestone_screenshot("datasets_tab")

        self.locate_profile_organizations_tab(page).click()
        expect(page).to_have_url(f"/user/{user['name']}/organizations")
        milestone_screenshot("organizations_tab")

        self.locate_profile_groups_tab(page).click()
        expect(page).to_have_url(f"/user/{user['name']}/groups")
        milestone_screenshot("groups_tab")

        self.locate_profile_tokens_tab(page).click()
        expect(page).to_have_url(f"/user/{user['name']}/api-tokens")
        milestone_screenshot("tokens_tab")

    @pytest.mark.ckan_standard("profile")
    def test_profile_management(
        self, milestone_screenshot: Any, login: Any, page: Page, user: dict[str, Any], faker: Faker
    ):
        """Test profile management flow.

        Given an authenticated user
        When they go to their profile page
        And click the "Manage" link
        And update their display name
        Then they are redirected back to their profile page
        And their new display name is shown in the header
        And the profile link with the old display name is no longer present
        And the user's display name is updated in the database
        """
        login(user["name"])

        page.goto(f"/user/{user['name']}")
        self.locate_profile_management_link(page).click()
        expect(page).to_have_url(f"/user/edit/{user['name']}")

        new_name = faker.name()
        page.get_by_label("full name").fill(new_name)
        milestone_screenshot("form_with_updad_field")

        self.locate_update_profile_button(page).click()
        expect(page).to_have_url(f"/user/{user['name']}")

        expect(self.locate_profile_link(page, user)).not_to_be_attached()

        user = call_action("user_show", id=user["id"])
        assert user["display_name"] == new_name
        expect(self.locate_profile_link(page, user)).to_be_visible()
        milestone_screenshot("updated_profile_page")


class StandardUser(Login, Logout, Profile):
    """Test generic authentication flow."""
