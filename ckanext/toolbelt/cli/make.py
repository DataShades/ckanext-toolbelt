import click

TPL_DEPS_MAKEFILE = """\
###############################################################################
#                             requirements: start                             #
###############################################################################
ckan_tag = ckan-2.9.3
ext_list = spatial

remote-spatial = https://github.com/ckan/ckanext-spatial.git branch master

###############################################################################
#                              requirements: end                              #
###############################################################################

_version = master

-include deps.mk

prepare:
	curl -O https://raw.githubusercontent.com/DataShades/ckan-deps-installer/$(_version)/deps.mk
"""


@click.group()
def make():
    """Generate, make, produce, print different things."""


@make.command()
def deps_makefile():
    """Print to stdout basic Makefile for ckan-deps-installer."""
    click.echo(TPL_DEPS_MAKEFILE)
