from pw.plugins.html_plugin import HTMLPlugin, _BookmarkHTMLParser

# ---------------------------------------------------------------------------
# _BookmarkHTMLParser unit tests
# ---------------------------------------------------------------------------


def test_parser_extracts_title_link_tags() -> None:
    parser = _BookmarkHTMLParser()
    parser.feed('<li title="dev,news"><a href="https://example.com">Example</a></li>')

    assert len(parser.entries) == 1
    title, link, tags = parser.entries[0]
    assert title == "Example"
    assert link == "https://example.com"
    assert tags == "dev,news"


def test_parser_handles_missing_li_title() -> None:
    """An <a> not wrapped in <li title="..."> should still be captured with empty tags."""
    parser = _BookmarkHTMLParser()
    parser.feed('<li><a href="https://example.com">No Tags</a></li>')

    assert len(parser.entries) == 1
    _, _, tags = parser.entries[0]
    assert tags == ""


def test_parser_multiple_entries() -> None:
    parser = _BookmarkHTMLParser()
    html = (
        '<li title="a"><a href="https://one.com">One</a></li>\n<li title="b"><a href="https://two.com">Two</a></li>\n'
    )
    parser.feed(html)

    assert len(parser.entries) == 2
    assert parser.entries[0][0] == "One"
    assert parser.entries[1][0] == "Two"


# ---------------------------------------------------------------------------
# HTMLPlugin.import_data
# ---------------------------------------------------------------------------


def test_html_import(tmp_path, session_factory, monkeypatch):
    plugin = HTMLPlugin()

    html = '<li title="admin"><a href="https://x/">Title</a></li>\n'
    input_file = tmp_path / "bookmarks.html"
    input_file.write_text(html)

    inserted = []

    def fake_insert(session, bookmark):
        inserted.append(bookmark)

    monkeypatch.setattr("pw.plugins.html_plugin.db.insert_bookmark", fake_insert)

    plugin.import_data(input_file, session_factory)

    assert len(inserted) == 1
    assert inserted[0].title == "Title"
    assert inserted[0].link == "https://x/"


def test_html_import_skips_entry_with_empty_title(tmp_path, session_factory, monkeypatch):
    """Entries whose title is empty after stripping are skipped."""
    plugin = HTMLPlugin()

    # The anchor text is whitespace only → stripped title is ""
    html = '<li title="dev"><a href="https://x/">   </a></li>\n'
    input_file = tmp_path / "bad.html"
    input_file.write_text(html)

    inserted = []

    def fake_insert(session, bookmark):
        inserted.append(bookmark)  # pragma: no cover

    monkeypatch.setattr("pw.plugins.html_plugin.db.insert_bookmark", fake_insert)

    plugin.import_data(input_file, session_factory)

    assert inserted == []


def test_html_import_skips_duplicate(tmp_path, session_factory, monkeypatch):
    """Entries that raise ValueError (duplicate link) are silently skipped."""
    plugin = HTMLPlugin()

    html = (
        '<li title="dev"><a href="https://x/">First</a></li>\n<li title="dev"><a href="https://x/">Duplicate</a></li>\n'
    )
    input_file = tmp_path / "dup.html"
    input_file.write_text(html)

    call_count = 0

    def fake_insert(session, bookmark):
        nonlocal call_count
        call_count += 1
        if call_count > 1:
            raise ValueError("duplicate")

    monkeypatch.setattr("pw.plugins.html_plugin.db.insert_bookmark", fake_insert)

    plugin.import_data(input_file, session_factory)

    assert call_count == 2


# ---------------------------------------------------------------------------
# HTMLPlugin.export_data
# ---------------------------------------------------------------------------


def test_html_export(tmp_path):
    from pw.bookmark import Bookmark

    plugin = HTMLPlugin()
    bookmarks = [
        Bookmark(id=1, title="Example", link="https://example.com", tags="dev;news"),
        Bookmark(id=2, title="No Tags", link="https://notags.com", tags=""),
    ]

    out = tmp_path / "bookmarks.html"
    plugin.export_data(out, bookmarks)

    lines = out.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 2
    assert '<li title="dev,news"><a href="https://example.com">Example</a></li>' == lines[0]
    assert '<li title=""><a href="https://notags.com">No Tags</a></li>' == lines[1]


def test_html_export_empty(tmp_path):
    plugin = HTMLPlugin()
    out = tmp_path / "empty.html"
    plugin.export_data(out, [])

    assert out.read_text(encoding="utf-8") == ""
