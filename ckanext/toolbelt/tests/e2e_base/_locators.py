from __future__ import annotations

from typing import Any

from playwright.sync_api import Page


class ElementLocator:
    def locate_login_link(self, page: Page):
        """Locate the "log in" link on the page."""
        return page.get_by_role("link", name="log in")

    def locate_logout_link(self, page: Page):
        """Locate the "log out" link on the page."""
        return page.get_by_label("log out")

    def locate_login_button(self, page: Page):
        """Locate the login button on the login page."""
        return page.get_by_role("button", name="login")

    def locate_profile_link(self, page: Page, user: dict[str, Any]):
        """Locate the profile link on the page based on the user's display name."""
        return page.get_by_text(user["display_name"]).first

    def locate_existing_login_session_alert(self, page: Page):
        """Locate the alert indicating an existing login session."""
        return page.get_by_text("you're already logged in").first

    def locate_logged_out_alert(self, page: Page):
        """Locate the alert indicating the user is logged out."""
        return page.get_by_text("you are now logged out").first

    def locate_main_area(self, page: Page):
        """Locate the main content area of the page."""
        return page.locator("[role=main]")

    def locate_profile_datasets_tab(self, page: Page):
        """Locate the "Datasets" link in the user's profile section."""
        return self.locate_main_area(page).get_by_role("link", name="Datasets")

    def locate_profile_organizations_tab(self, page: Page):
        """Locate the "Organizations" link in the user's profile section."""
        return self.locate_main_area(page).get_by_role("link", name="Organizations")

    def locate_profile_groups_tab(self, page: Page):
        """Locate the "Groups" link in the user's profile section."""
        return self.locate_main_area(page).get_by_role("link", name="Groups")

    def locate_profile_tokens_tab(self, page: Page):
        """Locate the "API Tokens" link in the user's profile section."""
        return self.locate_main_area(page).get_by_role("link", name="API Tokens")

    def locate_profile_management_link(self, page: Page):
        """Locate the "Manage" link in the user's profile section."""
        return self.locate_main_area(page).get_by_role("link", name="Manage")

    def locate_update_profile_button(self, page: Page):
        """Locate the "Update" button on the profile management page."""
        return page.get_by_role("button", name="update")
