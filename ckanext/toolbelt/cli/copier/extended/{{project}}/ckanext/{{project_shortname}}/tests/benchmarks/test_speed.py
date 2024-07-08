from __future__ import annotations

from typing import Any

import pytest

from ckan.plugins import plugin_loaded


@pytest.mark.benchmark()
@pytest.mark.usefixtures("with_plugins")
def test_plugin(benchmark: Any):
    benchmark(plugin_loaded, "{{ project_shortname }}")


@pytest.mark.benchmark()
@pytest.mark.usefixtures("with_plugins")
def test_plugin_with_spaces(benchmark: Any):
    benchmark(plugin_loaded, " {{ project_shortname }} ")
