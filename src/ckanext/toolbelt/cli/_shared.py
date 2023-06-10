from __future__ import annotations

import os
from string import Template
from typing import Any

import click

option_plugin = click.option(
    "-p",
    "--plugin",
    default="",
    help=(
        "Name of the target plugin."
        + " By default `ckanext-<PLUGIN>` part of the extension is used."
    ),
)

option_write = click.option(
    "-w",
    "--write",
    is_flag=True,
    help="Write output to the expected location instead of STDOUT",
)


def safe_plugin_name(plugin: str) -> str:
    if not plugin:
        plugin = os.path.basename(os.getcwd())
        if plugin.startswith("ckanext-"):
            plugin = plugin[8:]
    return plugin


def render(tpl: str, data: dict[str, Any] | None = None) -> str:
    source = os.path.join(os.path.dirname(__file__), "templates", tpl)
    with open(source) as stream:
        return Template(stream.read()).safe_substitute(**data or {})


def template_source(name: str) -> str:
    return f"template_{name}.toml"


def ensure_root():
    ext = os.path.basename(os.getcwd())
    if not ext.startswith("ckanext-"):
        click.secho(
            "Can be executed only from the root directory of the extension",
            fg="red",
        )
        raise click.Abort


def produce(src: str, dest: str, data: dict[str, Any], write: bool):
    content = render(src, data).strip()

    if write:
        with open(dest, "w") as file:
            click.echo(content, file)
    else:
        click.echo(content)
