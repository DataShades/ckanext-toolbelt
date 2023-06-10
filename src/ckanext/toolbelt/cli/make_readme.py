from __future__ import annotations

import textwrap
from typing import TYPE_CHECKING

import click

if TYPE_CHECKING:
    from ckan.config.declaration import Declaration


@click.group()
def readme():
    """Generate fragments for README.md."""


@readme.command()
@click.argument("plugins", nargs=-1)
def config(
    plugins: tuple[str, ...],
):
    """Print declared config options for the given plugins."""

    from ckan.config.declaration import Declaration
    from ckan.config.declaration.serialize import handler

    if not plugins:
        click.secho("At leas one plugin must be specified", fg="red")
        raise click.Abort
    handler.register("ckanext-readme")(_ckanext_readme)

    decl = Declaration()
    for name in plugins:
        decl.load_plugin(name)

    if decl:
        click.echo(handler.handle(decl, "ckanext-readme"))


def _ckanext_readme(declaration: Declaration):
    from ckan.config.declaration import Flag

    result = ""

    for item in declaration.iter_options():
        option = declaration[item]

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
