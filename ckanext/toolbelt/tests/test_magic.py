import sys
from types import ModuleType
from unittest.mock import Mock

from ckanext.toolbelt.magic import transfigure_xloaded_file


def test_transfigure_xloaded_file_forwards_loader_arguments(monkeypatch):
    loader = ModuleType("ckanext.xloader.loader")
    original_load_csv = Mock(return_value=["fields"])
    loader.load_csv = original_load_csv

    xloader = ModuleType("ckanext.xloader")
    xloader.loader = loader
    monkeypatch.setitem(sys.modules, "ckanext.xloader", xloader)
    monkeypatch.setitem(sys.modules, "ckanext.xloader.loader", loader)

    transform = Mock(return_value="/tmp/transformed.csv")
    transfigure_xloaded_file(transform)

    result = loader.load_csv(
        "/tmp/original.csv",
        "resource-id",
        mimetype="text/csv",
        allow_type_guessing=True,
        logger="logger",
    )

    assert result == ["fields"]
    transform.assert_called_once_with("/tmp/original.csv", "resource-id")
    original_load_csv.assert_called_once_with(
        "/tmp/transformed.csv",
        "resource-id",
        mimetype="text/csv",
        allow_type_guessing=True,
        logger="logger",
    )
