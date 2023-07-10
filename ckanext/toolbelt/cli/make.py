from __future__ import annotations

import click

from . import make_config, make_gh_action, make_readme, make_template


@click.group()
def make():
    """Generate, make, produce, print different things."""


make.add_command(make_readme.readme)
make.add_command(make_template.template)
make.add_command(make_gh_action.gh_action)
make.add_command(make_config.config)
