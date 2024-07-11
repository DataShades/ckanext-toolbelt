from __future__ import annotations
from configparser import NoSectionError
import contextlib
import os
import subprocess
import git
import click


TPL_DIR = os.path.join(os.path.dirname(__file__), "copier")
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
@click.option(
    "-f",
    "--overwrite",
    help="Overwrite existing extension.",
    is_flag=True,
)
@click.argument("project", default=PROJECT_PREFIX)
@click.option("-d", "--use-defaults", is_flag=True)
def extended(output_dir: str, overwrite: bool, project: str, use_defaults: bool):
    """Generate empty extension files to expand CKAN."""
    try:
        import copier
    except ImportError:
        subprocess.Popen(["pip", "install", "pipx"]).wait()
        subprocess.Popen(
            [
                "python",
                "-m",
                "pipx",
                "run",
                "ckanext-toolbelt[ckanext]",
                "make",
                "ckanext",
                "extended",
                project,
                "-o",
                output_dir,
            ]
            + (["-f"] if overwrite else [])
            + (["-d"] if use_defaults else [])
        ).wait()
        return

    template_loc = os.path.join(TPL_DIR, "extended")
    if not project.startswith(PROJECT_PREFIX):
        project = f"{PROJECT_PREFIX}{project}"

    if use_defaults and project == PROJECT_PREFIX:
        click.secho("Project must be specified", fg="red")
        raise click.Abort

    defaults = {"author": "", "author_email": "", "project": project}
    git_config = git.GitConfigParser()

    with contextlib.suppress(NoSectionError):
        defaults["author"] = git_config.get("user", "name")

    with contextlib.suppress(NoSectionError):
        defaults["author_email"] = git_config.get("user", "email")

    result = copier.run_copy(
        template_loc,
        output_dir,
        user_defaults=defaults,
        defaults=use_defaults,
        overwrite=overwrite,
        answers_file=".copier-answers.ctb-extended.yml",
        unsafe=True,
    )

    extension_path = os.path.realpath(
        os.path.join(output_dir, result.answers.combined["project"])
    )
    click.echo(f"Written: {extension_path}")
