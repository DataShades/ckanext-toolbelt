import pytest
import ckan.plugins.toolkit as tk
import ckan.tests.helpers as helpers


@pytest.mark.usefixtures("clean_db")
@pytest.mark.ckan_config("ckan.plugins", "toolbelt_safe_upload")
@pytest.mark.usefixtures("with_plugins")
class TestUserImageUrl(object):
    def test_external_picture(self):

        params = {
            "name": "test_user",
            "email": "test@example.com",
            "password": "12345678",
            "image_url": "https://example.com/mypic.png",
        }

        user_dict = helpers.call_action("user_create", {}, **params)

        assert user_dict["image_url"] == "https://example.com/mypic.png"
        assert (
            user_dict["image_display_url"] == "https://example.com/mypic.png"
        )

    def test_upload_non_picture_works_without_extra_config(
        self, create_with_upload, faker
    ):
        params = {
            "name": faker.user_name(),
            "email": faker.email(),
            "password": "12345678",
            "action": "user_create",
            "upload_field_name": "image_upload",
        }
        assert create_with_upload("hello world", "file.txt", **params)

    @pytest.mark.ckan_config("ckan.upload.user.types", "image")
    def test_upload_non_picture(self, create_with_upload, faker):
        params = {
            "name": faker.user_name(),
            "email": faker.email(),
            "password": "12345678",
            "action": "user_create",
            "upload_field_name": "image_upload",
        }
        with pytest.raises(
            tk.ValidationError, match="Unsupported upload type"
        ):
            create_with_upload("hello world", "file.txt", **params)

    @pytest.mark.ckan_config("ckan.upload.user.types", "image")
    def test_upload_non_picture_with_png_extension(
        self, create_with_upload, faker
    ):
        params = {
            "name": faker.user_name(),
            "email": faker.email(),
            "password": "12345678",
            "action": "user_create",
            "upload_field_name": "image_upload",
        }
        with pytest.raises(
            tk.ValidationError, match="Unsupported upload type"
        ):
            create_with_upload("hello world", "file.png", **params)

    @pytest.mark.ckan_config("ckan.upload.user.types", "image")
    def test_upload_picture(self, create_with_upload, faker):
        params = {
            "name": faker.user_name(),
            "email": faker.email(),
            "password": "12345678",
            "action": "user_create",
            "upload_field_name": "image_upload",
        }
        assert create_with_upload(faker.image(), "file.png", **params)
