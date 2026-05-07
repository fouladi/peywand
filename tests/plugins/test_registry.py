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


def test_register_duplicate_raises() -> None:
    """Registering a plugin with an already-used format name must raise."""

    class AnotherDummy:
        format = "dummy"  # same format as DummyPlugin registered above

        def import_data(self, path, session_factory): ...
        def export_data(self, path, bookmarks): ...

    with pytest.raises(ValueError, match="Plugin already registered: dummy"):
        register(AnotherDummy())
