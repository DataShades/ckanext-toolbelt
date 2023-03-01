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
