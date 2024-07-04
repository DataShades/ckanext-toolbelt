"""Tests for validators.py."""

import pytest

import ckan.plugins.toolkit as tk

from ckanext.{{project_shortname}}.logic import validators


def test_{{project_shortname}}_reauired_with_valid_value():
    assert validators.{{
        project_shortname}}_required("value") == "value"


def test_{{project_shortname}}_reauired_with_invalid_value():
    with pytest.raises(tk.Invalid):
        validators.{{project_shortname}}_required(None)
