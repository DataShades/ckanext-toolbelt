import pytest

from ckanext.toolbelt.utils.collector import Collector


class TestCollector:
    def fun(self):
        pass

    @pytest.mark.parametrize(
        ("prefix", "separator", "basic_name", "prefixed_name"),
        [
            ("", "_", "xxx", "fun"),
            ("toolbelt", "_", "xxx", "toolbelt_fun"),
            ("toolbelt", "-", "xxx", "toolbelt-fun"),
        ],
    )
    def test_basic(self, prefix, separator, basic_name, prefixed_name):
        collector, getter = Collector(prefix, separator).split()

        assert getter() == {}

        collector(basic_name)(self.fun)
        assert getter() == {basic_name: self.fun}

        collector(self.fun)
        assert getter() == {basic_name: self.fun, prefixed_name: self.fun}
