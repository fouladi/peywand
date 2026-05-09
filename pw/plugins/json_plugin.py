import json
from pathlib import Path

from pw import db
from pw.bookmark import Bookmark
from pw.plugins.io import ProgressCallback, report_progress
from pw.plugins.registry import register


class JSONPlugin:
    format = "json"

    def import_data(self, path: Path, session_factory, progress_callback: ProgressCallback | None = None) -> None:
        """Reads bookmark entries from a json file, extracts title,
        link, and tags, and inserts them into the database.
        """
        data = json.loads(path.read_text(encoding="utf-8"))

        if not isinstance(data, list):
            raise ValueError("Invalid JSON format")

        total = len(data)
        report_progress(progress_callback, 0, total)

        with session_factory() as session:
            for index, item in enumerate(data, start=1):
                try:
                    db.insert_bookmark(
                        session,
                        Bookmark(
                            id=None,
                            title=item["title"],
                            link=item["link"],
                            tags=item.get("tags", ""),
                        ),
                    )
                except KeyError, ValueError:
                    # Missing fields or duplicate entry
                    pass
                finally:
                    report_progress(progress_callback, index, total)

    def export_data(
        self,
        path: Path,
        bookmarks: list[Bookmark],
        progress_callback: ProgressCallback | None = None,
    ) -> None:
        """Export bookmarks to a JSON file.

        Args:
            path: Destination file path.
            bookmarks: List of bookmarks to export.

        Notes:
            - Existing files are overwritten.
            - UTF-8 encoding is always used.
        """
        total = len(bookmarks)
        report_progress(progress_callback, 0, total)

        payload = []
        for index, bookmark in enumerate(bookmarks, start=1):
            payload.append({"title": bookmark.title, "link": bookmark.link, "tags": bookmark.tags})
            report_progress(progress_callback, index, total)

        path.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )


register(JSONPlugin())
