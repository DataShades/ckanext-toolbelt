"""Tests for ckanext.{{ cookiecutter.project_shortname }}.logic.validators."""

import pytest

import ckan.plugins.toolkit as tk

from ckanext.{{ cookiecutter.project_shortname }}.logic import validators


def test_required_with_valid_value():
    """Non-empty value is accepted."""
    assert validators.{{
        cookiecutter.project_shortname}}_required("value") == "value"


def test_required_with_invalid_value():
    """Missing value is not accepted."""
    with pytest.raises(tk.Invalid):
        validators.{{ cookiecutter.project_shortname }}_required(None)


def test_complex():
    """Do something complex here."""
    key = ("name",)
    errors = {key: []}

    with pytest.raises(tk.StopOnError):
        validators.{{ cookiecutter.project_shortname }}_complex_validator(
            key,
            {key: tk.missing},
            errors,
            {},
        )

    assert errors[key] == ["Required"]
