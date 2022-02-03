import click

import ckan.model as model
import ckan.plugins.toolkit as tk
from ckan.lib.search import query_for, clear


@click.group(short_help="Extra tools for managing DB")
def db():
    pass

@db.command()
@click.option("-y", "--yes", is_flag=True)
def clean(yes: bool):
    if not yes:
        tk.error_shout("This command will erase data from your portal's DB.")
        tk.error_shout("All the datasets, organizations and users will be removed")
        tk.error_shout("Run it with `--yes` flag if you know what you are doing.")
        raise click.Abort()
    model.repo.delete_all()
