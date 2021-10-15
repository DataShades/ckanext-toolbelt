import click

from .make import make
from .dev import dev
from .search_index import search_index


@click.group(short_help="Variety of useful commands.")
def toolbelt():
    """Variety of useful commands."""


toolbelt.add_command(make)
toolbelt.add_command(dev)
toolbelt.add_command(search_index)
