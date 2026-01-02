from collections.abc import Callable
from pathlib import Path
from typing import Protocol

from pw.bookmark import Bookmark


class ImportExportPlugin(Protocol):
    format: str  # "html", "json", ...

    def import_data(self, path: Path, session_factory: Callable[[], object]) -> None: ...
    def export_data(self, path: Path, bookmarks: list[Bookmark]) -> None: ...
