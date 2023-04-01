from __future__ import annotations
import os
import textwrap
from string import Template
from typing import TYPE_CHECKING, Any

import click

if TYPE_CHECKING:
    from ckan.config.declaration import Declaration

TPL_DEPS_MAKEFILE = """\
###############################################################################
#                             requirements: start                             #
###############################################################################
ckan_tag = ckan-2.10.0
ext_list = spatial

remote-spatial = https://github.com/ckan/ckanext-spatial.git branch master

###############################################################################
#                              requirements: end                              #
###############################################################################

_version = master

-include deps.mk

prepare:
	curl -O {repo}/$(_version)/deps.mk
""".format(
    repo="https://raw.githubusercontent.com/DataShades/ckan-deps-installer"
)


TPL_RUFF_CONFIG = """\
[tool.ruff]
target-version = "py38"
"""

TPL_BLACK_CONFIG = """\
[tool.black]
# line-length = 88
# preview = true
"""

TPL_ISORT_CONFIG = """\
[tool.isort]
known_ckan = "ckan"
known_ckanext = "ckanext"
known_self = "ckanext.{plugin}"
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

strictParameterNoneValue = true

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
reportTypedDictNotRequiredAccess = false # Context won't work with this rule
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
reportUnusedCallResult = false # allow function calls for side-effect only
useLibraryCodeForTypes = true
reportGeneralTypeIssues = true
reportPropertyTypeMismatch = true
reportWildcardImportFromLibrary = true
reportUntypedClassDecorator = false
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
    """Print basic Makefile for ckan-deps-installer."""
    click.echo(TPL_DEPS_MAKEFILE)


@make.command()
def pyright_config(file: Any = None):
    """Print basic configuration of pyright."""
    click.echo(TPL_PYRIGHT_CONFIG, file)


@make.command()
def black_config(file: Any = None):
    """Print basic configuration of black."""
    click.echo(TPL_BLACK_CONFIG, file)


@make.command()
def ruff_config(file: Any = None):
    """Print basic configuration of ruff."""
    click.echo(TPL_RUFF_CONFIG, file)


@make.command()
@click.option("-p", "--plugin", default="")
def isort_config(plugin: str, file: Any = None):
    """Print basic configuration of isort."""
    plugin = _ensure_plugin(plugin)
    if not plugin:
        plugin = os.path.basename(os.getcwd())
        if plugin.startswith("ckanext-"):
            plugin = plugin[8:]
    click.echo(TPL_ISORT_CONFIG.format(plugin=plugin), file)


def _ensure_plugin(plugin: str):
    if not plugin:
        plugin = os.path.basename(os.getcwd())
        if plugin.startswith("ckanext-"):
            plugin = plugin[8:]
    return plugin


@make.command()
def pytest_config(file: Any = None):
    """Print basic configuration of pytest."""
    click.echo(TPL_PYTEST_CONFIG, file)


@make.command()
@click.option("-p", "--plugin", default="")
@click.option("-w", "--write", is_flag=True)
@click.pass_context
def pyproject(ctx: click.Context, plugin: str, write: bool):
    """Print simple pyproject example."""
    file = None
    if write:
        file = open("pyproject.toml", "w")

    ctx.invoke(black_config, file=file)
    ctx.invoke(ruff_config, file=file)
    ctx.invoke(isort_config, plugin=plugin, file=file)
    ctx.invoke(pytest_config, file=file)
    ctx.invoke(pyright_config, file=file)


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
    from ckan.config.declaration import Flag, Key

    result = ""

    for item in declaration._members:
        if not isinstance(item, Key):
            continue

        option = declaration._options[item]

        if option.has_flag(Flag.non_iterable()):
            continue

        if option.description:
            result += (
                textwrap.fill(
                    option.description,
                    width=77,
                    initial_indent="# ",
                    subsequent_indent="# ",
                )
                + "\n"
            )

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


@make.command()
@click.argument("action", type=click.Choice(["test", "pypi-publish"]))
@click.option("-p", "--plugin", default="")
@click.option("-w", "--write", is_flag=True)
def gh_action(action: str, plugin: str, write: bool):
    """Make GitHub actions.
    """
    plugin = os.path.basename(os.getcwd())
    if not plugin.startswith("ckanext-"):
        click.secho("Can be executed only from the root directory of the extension", fg="red")
        raise click.Abort()

    content = _render(f"action_{action}.yaml", {"PLUGIN": _ensure_plugin(plugin)})
    file = None
    if write:
        file = _action_file(action)

    click.echo(
        content,
        file
    )


def _render(tpl: str, data: dict[str, Any]) -> str:
    source = os.path.join(os.path.dirname(__file__), "templates", tpl)
    return Template(open(source).read()).safe_substitute(**data)

def _action_file(name: str) -> Any:
    path = ".github/workflows"
    os.makedirs(path, exist_ok=True)
    return open(os.path.join(path, f"{name}.yml"), "w")
