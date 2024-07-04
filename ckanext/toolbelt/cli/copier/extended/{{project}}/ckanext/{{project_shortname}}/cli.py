from __future__ import annotations

import click

from ckan import model

__all__ = ["{{ project_shortname }}"]


@click.group(short_help="{{project_shortname}} CLI.")
def {{ project_shortname }}():
    """{{project_shortname}} CLI."""


@{{ project_shortname }}.command()
@click.argument("name", default="{{project_shortname}}")
@click.option("-v", "--verbose", is_flag=True, help="Increase verbosity")
def command(name: str):
    """Docs."""
    click.echo(f"Hello, {name}!")


@{{ project_shortname }}.command()
def count_users():
    """Iterate over users and count something."""
    q = model.Session.query(model.User)
    total = 0

    with click.progressbar(q, q.count()) as bar:
        for _user in bar:
            total += 1

    click.secho(f"Result: {click.style(total, bold=True)}!")
