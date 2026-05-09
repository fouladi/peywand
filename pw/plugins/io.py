from collections.abc import Callable
from pathlib import Path
from typing import Protocol

from pw.bookmark import Bookmark

type ProgressCallback = Callable[[int, int | None], None]


def report_progress(progress_callback: ProgressCallback | None, completed: int, total: int | None) -> None:
    if progress_callback is not None:
        progress_callback(completed, total)


class ImportExportPlugin(Protocol):
    format: str  # "html", "json", ...

    def import_data(
        self,
        path: Path,
        session_factory: Callable[[], object],
        progress_callback: ProgressCallback | None = None,
    ) -> None: ...

    def export_data(
        self,
        path: Path,
        bookmarks: list[Bookmark],
        progress_callback: ProgressCallback | None = None,
    ) -> None: ...
