from html.parser import HTMLParser
from pathlib import Path

from pw import db
from pw.bookmark import Bookmark
from pw.plugins.io import ProgressCallback, report_progress
from pw.plugins.registry import register


class _BookmarkHTMLParser(HTMLParser):
    """Parse bookmark entries from an HTML file.

    Expected format per entry:

        <li title="tag1,tag2"><a href="https://example.com">Title</a></li>
    """

    def __init__(self) -> None:
        super().__init__()
        self.entries: list[tuple[str, str, str]] = []  # (title, link, tags)
        self._current_tags: str = ""
        self._current_link: str = ""
        self._in_anchor: bool = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_dict = dict(attrs)
        if tag == "li":
            self._current_tags = attrs_dict.get("title") or ""
        elif tag == "a":
            self._current_link = attrs_dict.get("href") or ""
            self._in_anchor = True

    def handle_data(self, data: str) -> None:
        if self._in_anchor and self._current_link:
            self.entries.append((data.strip(), self._current_link, self._current_tags))

    def handle_endtag(self, tag: str) -> None:
        if tag == "a":
            self._in_anchor = False
            self._current_link = ""


class HTMLPlugin:
    """Import/export bookmarks in HTML format.

    The HTML format uses one ``<li>`` element per bookmark:

        <li title="tag1,tag2"><a href="https://example.com">Title</a></li>

    This format is compatible with browser bookmark imports.
    """

    format = "html"

    def import_data(self, path: Path, session_factory, progress_callback: ProgressCallback | None = None) -> None:
        """Import bookmarks from an HTML file.

        Args:
            path: Path to the HTML input file.
            session_factory: Callable returning a DB session.

        Notes:
            - Invalid or incomplete entries are skipped silently.
            - Duplicate bookmarks are ignored.
        """
        parser = _BookmarkHTMLParser()
        parser.feed(path.read_text(encoding="utf-8"))

        total = len(parser.entries)
        report_progress(progress_callback, 0, total)

        with session_factory() as session:
            for index, (title, link, tags) in enumerate(parser.entries, start=1):
                try:
                    if not title or not link:
                        continue
                    db.insert_bookmark(
                        session,
                        Bookmark(id=None, title=title, link=link, tags=tags),
                    )
                except ValueError:
                    # Duplicate bookmark — skip silently
                    pass
                finally:
                    report_progress(progress_callback, index, total)

    def export_data(
        self,
        path: Path,
        bookmarks: list[Bookmark],
        progress_callback: ProgressCallback | None = None,
    ) -> None:
        """Export bookmarks to an HTML file.

        Args:
            path: Destination file path.
            bookmarks: List of bookmarks to export.

        Notes:
            - Existing files are overwritten.
            - UTF-8 encoding is always used.
            - Tag separators are normalised from ``;`` to ``,``.
        """
        total = len(bookmarks)
        report_progress(progress_callback, 0, total)

        with path.open("w", encoding="utf-8") as fh:
            for index, bookmark in enumerate(bookmarks, start=1):
                tags = bookmark.tags.replace(";", ",") if bookmark.tags else ""
                fh.write(f'<li title="{tags}"><a href="{bookmark.link}">{bookmark.title}</a></li>\n')
                report_progress(progress_callback, index, total)


register(HTMLPlugin())
