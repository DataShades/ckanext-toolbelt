from __future__ import annotations

from typing import Any

import pytest
from faker import Faker
from playwright.sync_api import Page, expect


class Login:
    @pytest.fixture
    def user_password(self, faker: Faker):
        """Pasword that can be overriden in subclasses."""
        return faker.password()

    @pytest.fixture
    def user__password(self, user_password: str):
        """Password for user fixture."""
        return user_password

    @pytest.mark.ckan_standard("login")
    def test_login_normal(self, page: Page, user: dict[str, Any], user_password: str):
        """Test normal login flow.

        Given an existing user
        When they go to the login page
        And fill in their username and password
        And submit the form
        Then they are redirected to the dashboard
        And their display name is shown in the header
        """
        page.goto("/")
        page.get_by_role("link", name="log in").click()
        expect(page).to_have_url("/user/login")

        page.get_by_label("username").fill(user["name"])
        page.get_by_label("password").fill(user_password)

        page.get_by_role("button", name="login").click()

        expect(page).to_have_url("/dashboard/datasets")
        expect(page.get_by_role("link", name=user["display_name"])).to_be_visible()

    def test_login_authenticated(self, login: Any, user: dict[str, Any], page: Page):
        """Authenticated user cannot access login page again.

        Given an authenticated user
        When they go to the login page
        Then they see a message that they are already logged in
        And the username and password fields are disabled
        """
        login(user["name"])

        expect(page.get_by_role("link", name="log in")).not_to_be_attached()
        page.goto("/user/login")

        expect(page.get_by_text("you're already logged in").first).to_be_visible()

        page.screenshot(path="/tmp/x.png")
        expect(page.get_by_label("username")).to_be_disabled()
        expect(page.get_by_label("password")).to_be_disabled()


class Logout:
    @pytest.mark.ckan_standard("logout", "login")
    def test_logout_normal(self, login: Any, user: dict[str, Any], page: Page, user_password: str):
        """Test normal logout flow.

        Given an authenticated user
        When they click the logout link
        Then they are redirected to the post-logout page
        And they see a message that they have been logged out
        And the login link is visible in the header
        """
        page.goto("/user/login")
        page.get_by_label("username").fill(user["name"])
        page.get_by_label("password").fill(user_password)

        page.get_by_role("button", name="login").click()

        page.get_by_role("link", name="log out").click()

        expect(page).to_have_url("/user/logged_out_redirect")
        expect(page.get_by_text("you are now logged out").first).to_be_visible()

        expect(page.get_by_role("link", name="log in")).to_be_visible()
        expect(page.get_by_role("link", name="log out")).not_to_be_attached()

    @pytest.mark.ckan_standard("logout", "login")
    def test_logout_anonymous(self, login: Any, page: Page):
        """Test anonymous user logout flow.

        Given an anonymous user
        When they go to the logout page
        Then they are redirected to the login page
        """
        page.goto("/user/_logout")
        expect(page).to_have_url("/user/login")


class Standard(Login, Logout):
    """Test generic authentication flow."""
