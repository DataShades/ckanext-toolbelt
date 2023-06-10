from __future__ import annotations

import os

import click

from . import _shared


@click.group()
def gh_action():
    """Make GitHub actions."""


@gh_action.command()
@_shared.option_plugin
@_shared.option_write
def test(plugin: str, write: bool):
    """Test workflow."""
    _shared.ensure_root()
    _shared.produce(
        "action_test.yaml",
        _action_file("test"),
        {"PLUGIN": _shared.safe_plugin_name(plugin)},
        write,
    )


@gh_action.command()
@_shared.option_plugin
@_shared.option_write
def pypi_publish(plugin: str, write: bool):
    """Publish package to PyPI when vX.Y.Z tag added."""
    _shared.ensure_root()
    _shared.produce(
        "action_pypi-publish.yaml",
        _action_file("pypi-publish"),
        {"PLUGIN": _shared.safe_plugin_name(plugin)},
        write,
    )


@gh_action.command()
@_shared.option_plugin
@_shared.option_write
def release_please(plugin: str, write: bool):
    """Create a PR that compiles changelog records and publishes GitHub release."""
    _shared.ensure_root()
    _shared.produce(
        "action_release-please.yaml",
        _action_file("release-please"),
        {"PLUGIN": _shared.safe_plugin_name(plugin)},
        write,
    )


def _action_file(name: str) -> str:
    path = ".github/workflows"
    os.makedirs(path, exist_ok=True)
    return os.path.join(path, f"{name}.yml")
