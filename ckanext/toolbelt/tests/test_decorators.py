import pytest

from ckanext.toolbelt import decorators


class TestCollector:
    def func(self):
        pass

    def test_basic(self):
        collector, getter = decorators.Collector().split()

        assert getter() == {}

        collector("xxx")(self.func)
        assert getter() == {"xxx": self.func}

        collector(self.func)
        assert getter() == {"xxx": self.func, "func": self.func}

    def test_prefix(self):
        collector, getter = decorators.Collector("toolbelt").split()

        assert getter() == {}

        collector("xxx")(self.func)
        assert getter() == {"xxx": self.func}

        collector(self.func)
        assert getter() == {"xxx": self.func, "toolbelt_func": self.func}

    def test_separator(self):
        collector, getter = decorators.Collector("toolbelt", "-").split()

        assert getter() == {}

        collector("xxx")(self.func)
        assert getter() == {"xxx": self.func}

        collector(self.func)
        assert getter() == {"xxx": self.func, "toolbelt-func": self.func}
