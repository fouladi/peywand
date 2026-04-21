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
