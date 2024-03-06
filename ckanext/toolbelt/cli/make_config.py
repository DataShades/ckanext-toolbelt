from __future__ import annotations

import click

from . import _shared


@click.group()
def config():
    """Make config files."""


@config.command()
@_shared.option_plugin
@_shared.option_write
def pyproject(plugin: str, write: bool):
    """pyproject.toml"""
    _shared.ensure_root()
    plugin = _shared.safe_plugin_name(plugin)
    data = {
        f"{part.upper()}_CONFIG": _shared.render(
            _shared.template_source(part),
            {"PLUGIN": plugin},
        )
        for part in ["black", "ruff", "isort", "pytest", "git_changelog", "pyright", "coverage"]
    }
    data["PLUGIN"] = plugin

    _shared.produce(*_config_files("pyproject"), data, write)


@config.command()
@_shared.option_plugin
@_shared.option_write
def pre_commit(plugin: str, write: bool):
    """Pre-commit (https://pre-commit.com/)"""
    _shared.ensure_root()
    _shared.produce(
        *_config_files("pre-commit"),
        {"PLUGIN": _shared.safe_plugin_name(plugin)},
        write,
    )


@config.command()
@_shared.option_plugin
@_shared.option_write
def ckanext_makefile(plugin: str, write: bool):
    """Tools for CKAN extension management"""
    _shared.ensure_root()
    _shared.produce(
        *_config_files("ckanext-makefile"),
        {"PLUGIN": _shared.safe_plugin_name(plugin)},
        write,
    )


@config.command()
@_shared.option_plugin
@_shared.option_write
def deps_makefile(plugin: str, write: bool):
    """CKAN dependency manager (https://github.com/DataShades/ckan-deps-installer)"""
    _shared.ensure_root()
    _shared.produce(
        *_config_files("deps-makefile"),
        {"PLUGIN": _shared.safe_plugin_name(plugin)},
        write,
    )


@config.command()
@_shared.option_plugin
@_shared.option_write
def gulp_sass(plugin: str, write: bool):
    """Gulpfile for SCSS-based assets"""
    _shared.ensure_root()
    _shared.produce(
        *_config_files("gulp-sass"),
        {"PLUGIN": _shared.safe_plugin_name(plugin)},
        write,
    )


def _config_files(name: str) -> tuple[str, str]:
    if name == "pyproject":
        return f"config_{name}.toml", "pyproject.toml"

    if name == "pre-commit":
        return f"config_{name}.yaml", ".pre-commit-config.yaml"

    if name == "deps-makefile":
        return f"config_{name}.sh", "Makefile"

    if name == "ckanext-makefile":
        return f"config_{name}.sh", "Makefile"

    if name == "gulp-sass":
        return f"config_{name}.js", "gulpfile.js"

    click.secho(f"Unsupported config: {name}", fg="red")
    raise click.Abort
