from __future__ import annotations

import io
from contextlib import redirect_stderr, redirect_stdout
from dataclasses import dataclass
from pathlib import Path

import pw.plugins  # noqa: F401
from pw import db
from pw.bookmark import Bookmark
from pw.plugins.registry import available_formats, get as get_plugin


@dataclass(slots=True, frozen=True)
class BookmarkFilters:
    title: str = ""
    link: str = ""
    tags: str = ""

    def tag_list(self) -> list[str] | None:
        tags = [tag.strip() for tag in self.tags.split(";") if tag.strip()]
        return tags or None


class BookmarkService:
    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self._engine, self.session_factory = db.create_engine_and_session(str(db_path))

    def initialize_database(self) -> None:
        db.create_database(str(self.db_path))

    def list_bookmarks(self, filters: BookmarkFilters | None = None) -> list[Bookmark]:
        current_filters = filters or BookmarkFilters()
        has_filters = any([current_filters.title, current_filters.link, current_filters.tag_list()])
        with self.session_factory() as session:
            rows = db.get_bookmarks_by_filter(
                session,
                title=current_filters.title or None,
                link=current_filters.link or None,
                tags=current_filters.tag_list(),
            )
            if not rows and not has_filters:
                rows = db.get_bookmarks_by_title(session)

        return sorted(rows or [], key=lambda bookmark: bookmark.title.casefold())

    def get_bookmark(self, bookmark_id: int) -> Bookmark:
        with self.session_factory() as session:
            return db.get_bookmark_by_id(session, bookmark_id)

    def add_bookmark(self, *, title: str, link: str, tags: str) -> Bookmark:
        bookmark = Bookmark(id=None, title=title, link=link, tags=tags)
        with self.session_factory() as session:
            db.insert_bookmark(session, bookmark)
            inserted = db.get_uniq_bookmark_by_filter(session, title=title, link=link, is_strict=True)
            if inserted is None:
                raise ValueError("Inserted bookmark could not be reloaded.")
            return inserted

    def update_bookmark(self, bookmark_id: int, *, title: str, link: str, tags: str) -> Bookmark:
        bookmark = Bookmark(id=None, title=title, link=link, tags=tags)
        with self.session_factory() as session:
            db.update_bookmark(session, bookmark_id, bookmark)
            return db.get_bookmark_by_id(session, bookmark_id)

    def delete_bookmark(self, bookmark_id: int) -> None:
        with self.session_factory() as session:
            db.delete_bookmark_by_id(session, bookmark_id)

    def import_bookmarks(self, *, path: Path, file_format: str) -> None:
        plugin = get_plugin(file_format)
        with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            plugin.import_data(path, self.session_factory)

    def export_bookmarks(self, *, path: Path, file_format: str, filters: BookmarkFilters | None = None) -> None:
        plugin = get_plugin(file_format)
        with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            plugin.export_data(path, self.list_bookmarks(filters))

    def available_formats(self) -> list[str]:
        return available_formats()

    def close(self) -> None:
        self._engine.dispose()
