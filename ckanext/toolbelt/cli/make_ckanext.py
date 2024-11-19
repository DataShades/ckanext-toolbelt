from __future__ import annotations
from configparser import NoSectionError
import contextlib
import os
import git
import click


TPL_DIR = os.path.join(os.path.dirname(__file__), "cookiecutter")
PROJECT_PREFIX = "ckanext-"


@click.group()
def ckanext():
    """Generate CKAN extension"""


@ckanext.command()
@click.option(
    "-o",
    "--output-dir",
    help="Location to put the generated template.",
    default=".",
)
@click.argument("project", default=PROJECT_PREFIX)
@click.option("-d", "--use-defaults", is_flag=True)
def extended(output_dir: str, project: str, use_defaults: bool):
    """Generate empty extension files to expand CKAN."""
    from cookiecutter.main import cookiecutter

    template_loc = os.path.join(TPL_DIR, "extended")
    if use_defaults and project == PROJECT_PREFIX:
        click.secho("Project must be specified", fg="red")
        raise click.Abort

    if project == PROJECT_PREFIX:
        project = click.prompt("Extension's name")
    if not project.startswith(PROJECT_PREFIX):
        project = f"{PROJECT_PREFIX}{project}"

    defaults = {
        "author": "",
        "author_email": "",
        "project": project,
        "project_shortname": project[8:].lower().replace("-", "_"),
        "github_user_name": "",
        "description": "",
    }
    defaults["plugin_class_name"] = (
        defaults["project_shortname"].title().replace("_", "") + "Plugin"
    )
    git_config = git.GitConfigParser()

    with contextlib.suppress(NoSectionError):
        defaults["author"] = git_config.get("user", "name")

    with contextlib.suppress(NoSectionError):
        defaults["author_email"] = git_config.get("user", "email")

    if not use_defaults:
        defaults["author"] = click.prompt("Author's name", default=defaults["author"])
        defaults["author_email"] = click.prompt(
            "Author's email",
            default=defaults["author_email"],
        )
        defaults["github_user_name"] = click.prompt(
            "Your Github user or organization name", default=""
        )
        defaults["description"] = click.prompt(
            "Brief description of the project",
            default="",
        )

    cookiecutter(
        template_loc,
        no_input=True,
        extra_context=defaults,
        output_dir=output_dir,
    )

    click.echo(f"Written: {output_dir}")
