from pathlib import Path

from pw.services import BookmarkFilters, BookmarkService


def test_service_crud_and_filtering(tmp_path: Path) -> None:
    service = BookmarkService(tmp_path / "peywand.db")
    try:
        service.initialize_database()

        first = service.add_bookmark(
            title="Hacker News",
            link="https://news.ycombinator.com",
            tags="dev;news",
        )
        service.add_bookmark(
            title="Python",
            link="https://python.org",
            tags="lang;docs",
        )

        rows = service.list_bookmarks(BookmarkFilters(tags="dev"))
        assert [bookmark.id for bookmark in rows] == [first.id]

        updated = service.update_bookmark(
            first.id or 0,
            title="HN",
            link="https://news.ycombinator.com",
            tags="dev;reading",
        )
        assert updated.title == "HN"

        fetched = service.get_bookmark(first.id or 0)
        assert fetched.tags == "dev;reading"

        service.delete_bookmark(first.id or 0)
        assert [bookmark.title for bookmark in service.list_bookmarks()] == ["Python"]
    finally:
        service.close()


def test_service_export_and_import_json(tmp_path: Path) -> None:
    source = BookmarkService(tmp_path / "source.db")
    target = BookmarkService(tmp_path / "target.db")
    try:
        source.initialize_database()
        source.add_bookmark(
            title="Example",
            link="https://example.com",
            tags="demo",
        )

        export_path = tmp_path / "bookmarks.json"
        source.export_bookmarks(path=export_path, file_format="json")
        assert export_path.exists()

        target.initialize_database()
        target.import_bookmarks(path=export_path, file_format="json")

        imported = target.list_bookmarks()
        assert len(imported) == 1
        assert imported[0].link == "https://example.com"
    finally:
        source.close()
        target.close()


def test_bookmark_filters_tag_list_returns_none_when_empty() -> None:
    """tag_list() must return None when the tags field is blank."""
    filters = BookmarkFilters(tags="")
    assert filters.tag_list() is None


def test_bookmark_filters_tag_list_returns_none_for_whitespace() -> None:
    """tag_list() must return None when tags contains only separators/spaces."""
    filters = BookmarkFilters(tags=";  ; ")
    assert filters.tag_list() is None


def test_bookmark_filters_tag_list_returns_list_when_set() -> None:
    filters = BookmarkFilters(tags="dev;news")
    result = filters.tag_list()
    assert result == ["dev", "news"]


def test_list_bookmarks_with_no_filters_returns_all(tmp_path: Path) -> None:
    """list_bookmarks() with empty filters falls back to returning all bookmarks."""
    service = BookmarkService(tmp_path / "peywand.db")
    try:
        service.initialize_database()
        service.add_bookmark(title="Alpha", link="https://alpha.com", tags="")
        service.add_bookmark(title="Beta", link="https://beta.com", tags="")

        rows = service.list_bookmarks()
        assert len(rows) == 2
        # Results are sorted by title
        assert [b.title for b in rows] == ["Alpha", "Beta"]
    finally:
        service.close()


def test_list_bookmarks_with_filters_no_match_returns_empty(tmp_path: Path) -> None:
    """list_bookmarks() with active filters that match nothing returns []."""
    service = BookmarkService(tmp_path / "peywand.db")
    try:
        service.initialize_database()
        service.add_bookmark(title="Alpha", link="https://alpha.com", tags="dev")

        rows = service.list_bookmarks(BookmarkFilters(title="zzz"))
        assert rows == []
    finally:
        service.close()
