from __future__ import annotations

import click

import ckan.model as model
import ckan.plugins.toolkit as tk


@click.group(short_help="Extra tools for managing DB")
def db():
    pass

@db.command()
@click.option("-y", "--yes", is_flag=True, help="Confirm your intention.")
@click.option("-k", "--keep", multiple=True, help="Tables that should not be cleaned")
def clean(yes: bool, keep: tuple[str]):
    if not yes:
        tk.error_shout("This command will erase data from your portal's DB.")
        tk.error_shout("All the datasets, organizations and users will be removed")
        tk.error_shout("Run it with `--yes` flag if you know what you are doing.")
        raise click.Abort()

    model.repo.session.remove()
    ## use raw connection for performance
    connection = model.repo.session.connection()
    tables = reversed(model.repo.metadata.sorted_tables)

    for table in tables:
        if table.name in keep:
            continue

        if not table.c:
            # skip `geometry_columns` or similar object from postgis
            continue

        if table.name == 'alembic_version':
            continue
        connection.execute('truncate "%s" cascade' % table.name)
    model.repo.session.commit()
    click.secho('Database table data deleted', fg="green")
