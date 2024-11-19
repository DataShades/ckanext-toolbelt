"""CLI commands for {{ cookiecutter.project }}.

Commands added to `__all__` attribute are added to main CKAN CLI.

Example:
    ```sh
    ckan {{ cookiecutter.project_shortname }} --help
    ```
"""

from __future__ import annotations

import click

from ckan import model

__all__ = ["{{ cookiecutter.project_shortname }}"]


# Register CLI group. Code of the group is executed whenever subcommand of this
# group is invoked. Usually, group body remains empty. But if all subcommands
# contain identical initialization process, consider describing it inside
# group.
@click.group(short_help="{{ cookiecutter.project_shortname }} CLI.")
@click.pass_context
def {{ cookiecutter.project_shortname }}(ctx: click.Context):
    """CLI commands of {{ cookiecutter.project_shortname }} plugin."""
    ctx.meta["{{ cookiecutter.project_shortname }}"] = "{{ cookiecutter.project_shortname }}"


# Command decorated with `{{ cookiecutter.project_shortname }}.command()` decorator is
# registered inside the group. Name of the command matches name of the function
# with underscores replaced by hyphens. You can pass string into `.command()`
# to use a different name of the command.
#
# `click.argument` defines positional argument of the command. `click.option`
# defines optional flag with the specified short and long names.
#
# `click.pass_context` passes shared contex object to the command. Example
# below uses it to read data set by initialization code from group body.
@{{ cookiecutter.project_shortname }}.command()
@click.argument("name", default="{{ cookiecutter.project_shortname }}")
@click.option("-v", "--verbose", count=True, help="Increase verbosity")
@click.pass_context
def command(ctx: click.Context, name: str, verbose: int):
    """Nunc porta vulputate tellus."""
    msg = f"Hello, {name or ctx.meta['{{ cookiecutter.project_shortname }}']}"
    if verbose:
        msg += "!" * verbose

    click.echo(msg)


# Command can execute arbitrary code. If you are writing command that processes
# a lot of records, wrap iteration over records into `click.progressbar`. It
# results in progressbar that shows estimated time required to complete the command.
#
# When printing something, always use `click.echo` for plain output and
# `click.secho` for styled(colored) output. Never use built-in `print`
# function. It's allowed to use logging, but most likely, you don't need and
# `click.echo` is much better choice.
@{{ cookiecutter.project_shortname }}.command()
def count_users():
    """Iterate over users and count something."""
    q = model.Session.query(model.User)
    total = 0

    with click.progressbar(q, q.count()) as bar:
        for _user in bar:
            total += 1

    click.secho(f"Result: {click.style(total, bold=True)}!")
