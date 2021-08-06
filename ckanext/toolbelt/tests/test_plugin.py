import pytest
import ckan.plugins as p


@pytest.mark.usefixtures("with_plugins")
def test_plugin():
    assert p.plugin_loaded("toolbelt")
