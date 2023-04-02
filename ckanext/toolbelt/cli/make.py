from __future__ import annotations

import os
import textwrap
from string import Template
from typing import TYPE_CHECKING, Any, Optional

import click

if TYPE_CHECKING:
    from ckan.config.declaration import Declaration


@click.group()
def make():
    """Generate, make, produce, print different things."""


def _safe_plugin_name(plugin: str) -> str:
    if not plugin:
        plugin = os.path.basename(os.getcwd())
        if plugin.startswith("ckanext-"):
            plugin = plugin[8:]
    return plugin


@make.command()
@click.argument("plugins", nargs=-1)
def config_readme(
    plugins: tuple[str, ...],
):
    """Print declared config options for the given plugins in READE.md format."""

    from ckan.cli.config import _declaration
    from ckan.config.declaration.serialize import handler

    handler.register("ckanext-readme")(_ckanext_readme)

    decl = _declaration(plugins, False, False)
    if decl:
        click.echo(handler.handle(decl, "ckanext-readme"))


def _ckanext_readme(declaration: "Declaration"):
    from ckan.config.declaration import Flag, Key

    result = ""

    for item in declaration._members:
        if not isinstance(item, Key):
            continue

        option = declaration._options[item]

        if option.has_flag(Flag.non_iterable()):
            continue

        if option.description:
            result += (
                textwrap.fill(
                    option.description,
                    width=77,
                    initial_indent="# ",
                    subsequent_indent="# ",
                )
                + "\n"
            )

        if not option.has_default():
            value = option.placeholder or ""
        elif isinstance(option.default, bool):
            value = option.str_value().lower()
        else:
            value = option.str_value()

        if not option.has_flag(Flag.required):
            result += f"# (optional, default: {value})\n"

        result += f"{item} = {option.example or value}\n\n"

    return result


@make.command()
@click.argument(
    "template", type=click.Choice(["black", "isort", "pyright", "pytest", "ruff"])
)
@click.option("-p", "--plugin", default="")
@click.option("-f", "--file", type=click.File("a"))
def template(template: str, plugin: str, file: Optional[Any]):
    _ensure_root()
    content = _render(_template_source(template), {"PLUGIN": _safe_plugin_name(plugin)})
    click.echo(content, file)


def _template_source(name: str) -> str:
    return f"template_{name}.toml"


def _ensure_root():
    ext = os.path.basename(os.getcwd())
    if not ext.startswith("ckanext-"):
        click.secho(
            "Can be executed only from the root directory of the extension", fg="red"
        )
        raise click.Abort()


@make.command()
@click.argument("action", type=click.Choice(["test", "pypi-publish", "release-please"]))
@click.option("-p", "--plugin", default="")
@click.option("-w", "--write", is_flag=True)
def gh_action(action: str, plugin: str, write: bool):
    """Make GitHub actions."""
    _ensure_root()

    content = _render(f"action_{action}.yaml", {"PLUGIN": _safe_plugin_name(plugin)})
    file = None
    if write:
        file = _action_file(action)

    click.echo(content, file)


def _render(tpl: str, data: Optional[dict[str, Any]] = None) -> str:
    source = os.path.join(os.path.dirname(__file__), "templates", tpl)
    return Template(open(source).read()).safe_substitute(**data or {})


def _action_file(name: str) -> Any:
    path = ".github/workflows"
    os.makedirs(path, exist_ok=True)
    return open(os.path.join(path, f"{name}.yml"), "w")


@make.command()
@click.argument(
    "config", type=click.Choice(["pyproject", "pre-commit", "deps-makefile"])
)
@click.option("-p", "--plugin", default="")
@click.option("-w", "--write", is_flag=True)
@click.pass_context
def config(ctx: click.Context, config: str, plugin: str, write: bool):
    """Make GitHub actions."""
    _ensure_root()
    src, dest = _config_files(config)

    file = None
    if write:
        file = open(dest, "w")

    data = {"PLUGIN": _safe_plugin_name(plugin)}

    if config == "pyproject":
        for part in ["black", "ruff", "isort", "pytest", "pyright"]:
            data[f"{part.upper()}_CONFIG"] = _render(_template_source(part), data)

    content = _render(src, data)
    click.echo(content, file)


def _config_files(name: str) -> tuple[str, str]:
    if name == "pyproject":
        return f"config_{name}.toml", "pyproject.toml"

    if name == "pre-commit":
        return f"config_{name}.yaml", ".pre-commit-config.yaml"

    if name == "deps-makefile":
        return f"config_{name}.sh", "Makefile"

    click.secho(f"Unsupported config: {name}", fg="red")
    raise click.Abort()
