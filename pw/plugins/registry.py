from pw.plugins.io import ImportExportPlugin

_PLUGINS: dict[str, ImportExportPlugin] = {}


def register(plugin: ImportExportPlugin) -> None:
    if plugin.format in _PLUGINS:
        raise ValueError(f"Plugin already registered: {plugin.format}")
    _PLUGINS[plugin.format] = plugin


def get(format_name: str) -> ImportExportPlugin:
    try:
        return _PLUGINS[format_name]
    except KeyError:
        raise ValueError(f"Unknown file format: {format_name}")


def available_formats() -> list[str]:
    return sorted(_PLUGINS)
