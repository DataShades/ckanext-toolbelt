from __future__ import annotations

import logging
import os
import tempfile
from typing import Optional

import requests

import ckan.plugins as p
from ckan.lib.uploader import get_resource_uploader

log = logging.getLogger(__name__)

DEFAULT_DOWNLOAD_TIMEOUT = 2


class StaticPath:
    def __init__(self, path: Optional[str]):
        self.path = path

    def __bool__(self):
        return bool(self.path)

    def __enter__(self):
        return self.path

    def __exit__(self, type_, value, traceback):
        pass


class RemovablePath(StaticPath):
    def __exit__(self, type_, value, traceback):
        if self.path:
            os.remove(self.path)


def path_to_resource(res, max_size: int = 0) -> StaticPath:
    """Returns a filepath for a resource that will be indexed"""
    res_id = res["id"]
    res_url = res["url"]

    if res["url_type"] == "upload":
        uploader = get_resource_uploader(res)

        # TODO temporary workaround for ckanext-cloudstorage support
        if p.plugin_loaded("cloudstorage"):
            url = uploader.get_url_from_filename(res_id, res_url)
            filepath = _download_remote_file(res_id, url, max_size)
            return RemovablePath(filepath)

        path = uploader.get_path(res_id)
        if not os.path.exists(path):
            log.warning('Resource "%s" refers to unexisting path "%s"', res, path)
            return StaticPath(None)

        return StaticPath(path)

    if max_size > 0:
        filepath = _download_remote_file(res_id, res_url, max_size)
        return RemovablePath(filepath)

    return StaticPath(None)


def _download_remote_file(res_id: str, url: str, max_size: int) -> Optional[str]:
    """
    Downloads remote resource and save it as temporary file
    Returns path to this file
    """

    try:
        resp = requests.get(
            url,
            timeout=DEFAULT_DOWNLOAD_TIMEOUT,
            stream=True,
            headers={"user-agent": "python/toolbelt"},
        )
    except Exception as e:
        log.warning(
            "Unable to make GET request for resource %s with url <%s>: %s",
            res_id,
            url,
            e,
        )
        return

    if not resp.ok:
        log.warning(
            "Unsuccessful GET request for resource %s with url <%s>. \
            Status code: %s",
            res_id,
            url,
            resp.status_code,
        )
        return

    try:
        size = int(resp.headers.get("content-length", 0))
    except ValueError:
        log.warning("Incorrect Content-length header from url <%s>", url)
        return

    if not size:
        log.debug("Cannot determine size")
        return

    if size > max_size:
        log.debug("File exceeds allowed size(%d): %d", max_size, size)
        return

    dest = tempfile.NamedTemporaryFile(delete=False)
    try:
        with dest:
            for chunk in resp.iter_content(1024 * 64):
                dest.write(chunk)
    except requests.exceptions.RequestException as e:
        log.error("Cannot index remote resource %s with url <%s>: %s", res_id, url, e)
        os.remove(dest.name)
        return
    return dest.name
