from __future__ import annotations

import os
from typing import Optional
import uuid
import magic

import ckan.plugins as p
import ckan.plugins.toolkit as tk
import ckan.lib.uploader as uploader


class SafeUploadPlugin(p.SingletonPlugin):
    p.implements(p.IUploader, inherit=True)

    # IUploader

    def get_resource_uploader(self, data_dict):
        for plugin in p.PluginImplementations(p.IUploader):
            if isinstance(plugin, type(self)):
                continue
            return plugin.get_resource_uploader(data_dict)

    def get_uploader(self, upload_to, old_filename=None):
        return SafeUpload(upload_to, old_filename)


class SafeUpload(uploader.Upload):
    storage_path: str
    filename: Optional[str]

    def update_data_dict(self, data_dict, url_field, file_field, clear_field):
        super(SafeUpload, self).update_data_dict(
            data_dict, url_field, file_field, clear_field
        )
        if self.filename:
            self.verify_type()

            self.filename = str(uuid.uuid3(uuid.NAMESPACE_DNS, self.filename))
            self.filepath = os.path.join(self.storage_path, self.filename)
            data_dict[url_field] = self.filename

    def verify_type(self):
        if not self.filename:
            return

        actual = magic.from_buffer(self.upload_file.read(1024), mime=True)
        self.upload_file.seek(0, os.SEEK_SET)

        err = {self.file_field: [f"Unsupported upload type: {actual}"]}

        mimetypes = tk.aslist(
            tk.config.get(f"ckan.upload.{self.object_type}.mimetypes")
        )
        if mimetypes and actual not in mimetypes:
            raise tk.ValidationError(err)

        type_ = actual.split("/")[0]
        types = tk.aslist(
            tk.config.get(f"ckan.upload.{self.object_type}.types")
        )
        if types and type_ not in types:
            raise tk.ValidationError(err)
