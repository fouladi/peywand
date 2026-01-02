import json
from pathlib import Path

from tqdm import tqdm

from pw import db
from pw.bookmark import Bookmark
from pw.plugins.registry import register


class JSONPlugin:
    format = "json"

    def import_data(self, path: Path, session_factory) -> None:
        """Reads bookmark entries from a json file, extracts title,
        link, and tags, and inserts them into the database.
        """
        data = json.loads(path.read_text(encoding="utf-8"))

        if not isinstance(data, list):
            raise ValueError("Invalid JSON format")

        with (
            session_factory() as session,
            tqdm(total=len(data), desc="Importing JSON bookmarks") as bar,
        ):
            for item in data:
                bar.update(1)
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
                except (KeyError, ValueError):
                    pass

    def export_data(self, path: Path, bookmarks: list[Bookmark]) -> None:
        payload = [{"title": b.title, "link": b.link, "tags": b.tags} for b in bookmarks]
        path.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )


register(JSONPlugin())
