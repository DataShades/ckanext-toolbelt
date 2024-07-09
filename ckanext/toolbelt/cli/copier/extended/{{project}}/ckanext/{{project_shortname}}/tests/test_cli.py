"""Tests for ckanext.{{ project_shortname }}.cli module.

Use `cli` fixture to invoke CLI commands.
"""

from __future__ import annotations

from typing import Any

from click.testing import CliRunner
from faker import Faker

from ckan import model

import ckanext.{{ project_shortname }}.cli as commands


class TestCommand:
    """Test `heh command` CLI command."""

    def test_output(self, cli: CliRunner, faker: Faker):
        """Command prints expected message."""
        # it's possible to execute `commands.command` directly, but group
        # contains initialization logic and `commands.command` will fail
        # without it
        #
        # Any parameter specified after the command must be passed inside a
        # second argument of `cli.invoke`. For example, `{{project_shortname}}
        # a b -C 1 --xxx=2` becomes `cli.invoke({{ project_shortname }}, ["a",
        # "b", "-C", "1", "--xxx=2"])`
        result = cli.invoke(commands.{{ project_shortname }}, ["command"])
        # `result.exit_code` contains `0` if command succeeded
        assert not result.exit_code
        # `result.output` contains normal output. `result.stderr` contains
        # output of an error
        assert result.output == "Hello, {{ project_shortname }}\n"

        # use fake data instead of hardcoded test values to discover
        # output-based problems
        name = faker.word()
        result = cli.invoke(commands.{{ project_shortname }}, ["command", name])
        assert result.output == f"Hello, {name}\n"

    def test_verbosity(self, cli: CliRunner):
        """Verbosity level appends exclamation marks."""
        result = cli.invoke(commands.{{ project_shortname }}, ["command", "-v"])
        assert result.output == "Hello, {{ project_shortname }}!\n"

        result = cli.invoke(commands.{{ project_shortname }}, ["command", "-vvv"])
        assert result.output == "Hello, {{ project_shortname }}!!!\n"


class TestCountUsers:
    """Test `heh count-users` CLI command."""

    def test_output(self, cli: CliRunner, faker: Faker, user_factory: Any):
        """Command counts number of users in DB."""
        result = cli.invoke(commands.{{ project_shortname }}, ["count-users"])
        count = model.User.count()
        assert result.output == f"\nResult: {count}!\n"

        # create a new user to verify that we are not receiving static result
        user_factory()

        result = cli.invoke(commands.{{ project_shortname }}, ["count-users"])
        count = model.User.count()
        assert result.output == f"\nResult: {count}!\n"
