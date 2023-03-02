from __future__ import annotations
import textwrap
from collections.abc import Iterable
from typing import TYPE_CHECKING

import click

if TYPE_CHECKING:
    from ckan.config.declaration import Declaration

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

TPL_BLACK_CONFIG = """\
[tool.black]
line-length = 79
preview = true
"""

TPL_ISORT_CONFIG = """\
[tool.isort]
known_ckan = "ckan"
known_ckanext = "ckanext"
known_self = "ckanext{plugin}"
sections = "FUTURE,STDLIB,FIRSTPARTY,THIRDPARTY,CKAN,CKANEXT,SELF,LOCALFOLDER"
"""
TPL_PYTEST_CONFIG = """\
[tool.pytest.ini_options]
addopts = "--ckan-ini test.ini"
filterwarnings = [
               "ignore::sqlalchemy.exc.SADeprecationWarning",
               "ignore::sqlalchemy.exc.SAWarning",
               "ignore::DeprecationWarning",
]
"""

TPL_PYRIGHT_CONFIG = """\
[tool.pyright]
pythonVersion = "3.7"
include = ["ckanext"]
exclude = [
    "**/test*",
    "**/migration",
]
strict = []

strictParameterNoneValue = true # type must be Optional if default value is None

# Check the meaning of rules here
# https://github.com/microsoft/pyright/blob/main/docs/configuration.md
reportFunctionMemberAccess = true # non-standard member accesses for functions
reportMissingImports = true
reportMissingModuleSource = true
reportMissingTypeStubs = false
reportImportCycles = true
reportUnusedImport = true
reportUnusedClass = true
reportUnusedFunction = true
reportUnusedVariable = true
reportDuplicateImport = true
reportOptionalSubscript = true
reportOptionalMemberAccess = true
reportOptionalCall = true
reportOptionalIterable = true
reportOptionalContextManager = true
reportOptionalOperand = true
reportTypedDictNotRequiredAccess = false # We are using Context in a way that conflicts with this check
reportConstantRedefinition = true
reportIncompatibleMethodOverride = true
reportIncompatibleVariableOverride = true
reportOverlappingOverload = true
reportUntypedFunctionDecorator = false
reportUnknownParameterType = true
reportUnknownArgumentType = false
reportUnknownLambdaType = false
reportUnknownMemberType = false
reportMissingTypeArgument = true
reportInvalidTypeVarUse = true
reportCallInDefaultInitializer = true
reportUnknownVariableType = true
reportUntypedBaseClass = true
reportUnnecessaryIsInstance = true
reportUnnecessaryCast = true
reportUnnecessaryComparison = true
reportAssertAlwaysTrue = true
reportSelfClsParameterName = true
reportUnusedCallResult = false # allow function calls for side-effect only (like logic.check_acces)
useLibraryCodeForTypes = true
reportGeneralTypeIssues = true
reportPropertyTypeMismatch = true
reportWildcardImportFromLibrary = true
reportUntypedClassDecorator = false # authenticator relies on repoze.who class-decorator
reportUntypedNamedTuple = true
reportPrivateUsage = true
reportPrivateImportUsage = true
reportInconsistentConstructor = true
reportMissingSuperCall = false
reportUninitializedInstanceVariable = true
reportInvalidStringEscapeSequence = true
reportMissingParameterType = true
reportImplicitStringConcatenation = false
reportUndefinedVariable = true
reportUnboundVariable = true
reportInvalidStubStatement = true
reportIncompleteStub = true
reportUnsupportedDunderAll = true
reportUnusedCoroutine = true
reportUnnecessaryTypeIgnoreComment = true
reportMatchNotExhaustive = true
"""

@click.group()
def make():
    """Generate, make, produce, print different things."""


@make.command()
def deps_makefile():
    """Print to stdout basic Makefile for ckan-deps-installer."""
    click.echo(TPL_DEPS_MAKEFILE)


@make.command()
def pyright_config():
    """Print to stdout basic configuration of pyright."""
    click.echo(TPL_PYRIGHT_CONFIG)

@make.command()
def black_config():
    """Print to stdout basic configuration of black."""
    click.echo(TPL_BLACK_CONFIG)


@make.command()
@click.option("-p", "--plugin", default="")
def isort_config(plugin: str):
    """Print to stdout basic configuration of isort."""
    click.echo(TPL_ISORT_CONFIG.format(plugin=f".{plugin}"))

@make.command()
def pytest_config():
    """Print to stdout basic configuration of pytest."""
    click.echo(TPL_PYTEST_CONFIG)



@make.command()
@click.option("-p", "--plugin", default="")
@click.pass_context
def pyproject(ctx: click.Context, plugin: str):
    """Print to stdout simple pyproject example."""
    ctx.invoke(black_config)
    ctx.forward(isort_config)
    ctx.invoke(pytest_config)
    ctx.invoke(pyright_config)


@make.command()
@click.argument("plugins", nargs=-1)
def config_readme(
    plugins: tuple[str, ...],
):
    """Print declared config options for the given plugins in READE.md format."""

    from ckan.cli.config import _declaration
    from ckan.config.declaration.serialize import handler
    handler.register("ckanext-readme")(_ckanext_readme)

    decl = _declaration(plugins, False, False)
    if decl:
        click.echo(handler.handle(decl, "ckanext-readme"))



def _ckanext_readme(declaration: "Declaration"):
    from ckan.config.declaration import Key, Flag

    result = ""

    for item in declaration._members:
        if not isinstance(item, Key):
            continue

        option = declaration._options[item]


        if option.has_flag(Flag.non_iterable()):
            continue

        if option.description:
            result += textwrap.fill(option.description, width=77, initial_indent="# ", subsequent_indent="# ") + "\n"

        if not option.has_default():
            value = option.placeholder or ""
        elif isinstance(option.default, bool):
            value = option.str_value().lower()
        else:
            value = option.str_value()

        if not option.has_flag(Flag.required):
            result += f"# (optional, default: {value})\n"


        result += f"{item} = {option.example or value}\n\n"

    return result
