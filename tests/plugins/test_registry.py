import pytest

from pw.plugins.registry import get, register


class DummyPlugin:
    format = "dummy"

    def import_data(self, path, session_factory): ...
    def export_data(self, path, bookmarks): ...


def test_register_and_get_plugin():
    plugin = DummyPlugin()
    register(plugin)

    retrieved = get("dummy")
    assert retrieved is plugin


def test_unknown_plugin():
    with pytest.raises(ValueError):
        get("does-not-exist")
