import click

from .make import make
from .dev import dev

@click.group(short_help="Variety of useful commands.")
def toolbelt():
    """Variety of useful commands."""


toolbelt.add_command(make)
toolbelt.add_command(dev)
