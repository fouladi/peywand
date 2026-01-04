import re
from pathlib import Path

from tqdm import tqdm

from pw import db
from pw.bookmark import Bookmark
from pw.plugins.registry import register

REG_TITLE = re.compile(r"^>(.*?)<")


class HTMLPlugin:
    format = "html"

    def import_data(self, path: Path, session_factory) -> None:
        """Reads bookmark entries line by line, extracts title, link,
        and tags, and inserts them into the database. The format a read
        line is like:

        <li title="admin"><a href="https://statuses.now.sh/">HTTP Status</a></li>
        """
        total = sum(1 for _ in path.open(encoding="utf-8"))

        with (
            session_factory() as session,
            path.open(encoding="utf-8") as fh,
            tqdm(total=total, desc="Importing HTML bookmarks") as bar,
        ):
            for line in fh:
                bar.update(1)
                parts = line.split('"')
                if len(parts) < 5:
                    continue

                match = REG_TITLE.search(parts[4])
                if not match:
                    continue

                try:
                    db.insert_bookmark(
                        session,
                        Bookmark(
                            id=None,
                            title=match.group(1),
                            link=parts[3],
                            tags=parts[1],
                        ),
                    )
                except ValueError:
                    pass

    def export_data(self, path: Path, bookmarks: list[Bookmark]) -> None:
        """Writes all bookmarks to the specified output file in a format
        compatible with browser bookmark imports. The format of a
        written line is like:

        <li title="admin"><a href="https://statuses.now.sh/">HTTP Status</a></li>
        """
        with (
            path.open("w", encoding="utf-8") as fh,
            tqdm(total=len(bookmarks), desc="Exporting HTML bookmarks") as bar,
        ):
            for b in bookmarks:
                tags = b.tags.replace(";", ",") if b.tags else ""
                fh.write(f'<li title="{tags}"><a href="{b.link}">{b.title}</a></li>\n')
                bar.update(1)


register(HTMLPlugin())
