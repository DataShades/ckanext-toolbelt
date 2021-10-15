import click

import ckan.model as model
import ckan.plugins.toolkit as tk
from ckan.lib.search import query_for, clear


@click.group(short_help="Extra tools for managing search-index")
def search_index():
    pass


@search_index.command()
@click.option("-y", "--no-confirm", is_flag=True)
@click.pass_context
def clear_missing(ctx, no_confirm: bool):
    q = query_for("package")
    with ctx.meta["flask_app"].test_request_context():
        limit = tk.get_action("package_search")(
            {"ignore_auth": True}, {"rows": 0}
        )["count"]
    with click.progressbar(q.get_all_entity_ids(limit)) as bar:
        query = model.Session.query(model.Package.id)
        ids = {
            id
            for id in bar
            if not model.Session.query(
                query.filter_by(id=id).exists()
            ).scalar()
        }

    if not ids:
        click.secho("No missing packages detected", fg="green")
        return

    click.echo("Following packages are missing from the database:")
    for id in ids:
        click.echo("\t" + id)

    if not no_confirm:
        abort = not click.confirm(
            "Do you want to remove these packages from the search index?"
        )
        if abort:
            raise click.Abort()

    for id in ids:
        clear(id)
