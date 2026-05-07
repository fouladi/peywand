import json

import pytest

from pw.plugins.json_plugin import JSONPlugin


def test_json_export(tmp_path):
    plugin = JSONPlugin()

    bookmarks: list = [type("B", (), {"title": "T", "link": "L", "tags": "x"})()]

    out = tmp_path / "bookmarks.json"
    plugin.export_data(out, bookmarks)

    data = json.loads(out.read_text())
    assert data == [{"title": "T", "link": "L", "tags": "x"}]


def test_json_import(tmp_path, session_factory, monkeypatch):
    plugin = JSONPlugin()

    input_file = tmp_path / "in.json"
    input_file.write_text(json.dumps([{"title": "T", "link": "L", "tags": "x"}]))

    inserted = []

    def fake_insert(session, bookmark):
        inserted.append(bookmark)

    monkeypatch.setattr("pw.plugins.json_plugin.db.insert_bookmark", fake_insert)

    plugin.import_data(input_file, session_factory)

    assert len(inserted) == 1
    assert inserted[0].title == "T"


def test_json_import_raises_on_non_list(tmp_path, session_factory):
    """If the JSON root is not a list, ValueError is raised."""
    plugin = JSONPlugin()

    input_file = tmp_path / "bad.json"
    input_file.write_text('{"title": "Not a list"}')

    with pytest.raises(ValueError, match="Invalid JSON format"):
        plugin.import_data(input_file, session_factory)


def test_json_import_skips_entry_with_missing_key(tmp_path, session_factory, monkeypatch):
    """Entries missing required keys are silently skipped."""
    plugin = JSONPlugin()

    input_file = tmp_path / "missing.json"
    # Second entry is missing 'link'
    input_file.write_text(json.dumps([{"title": "Valid", "link": "https://x.com"}, {"title": "No Link"}]))

    inserted = []

    def fake_insert(session, bookmark):
        inserted.append(bookmark)

    monkeypatch.setattr("pw.plugins.json_plugin.db.insert_bookmark", fake_insert)

    plugin.import_data(input_file, session_factory)

    assert len(inserted) == 1
    assert inserted[0].title == "Valid"


def test_json_import_skips_duplicate(tmp_path, session_factory, monkeypatch):
    """Entries that raise ValueError (duplicate link) are silently skipped."""
    plugin = JSONPlugin()

    input_file = tmp_path / "dup.json"
    input_file.write_text(
        json.dumps([{"title": "First", "link": "https://x.com"}, {"title": "Duplicate", "link": "https://x.com"}])
    )

    call_count = 0

    def fake_insert(session, bookmark):
        nonlocal call_count
        call_count += 1
        if call_count > 1:
            raise ValueError("duplicate")

    monkeypatch.setattr("pw.plugins.json_plugin.db.insert_bookmark", fake_insert)

    plugin.import_data(input_file, session_factory)

    assert call_count == 2


def test_json_export_empty(tmp_path):
    plugin = JSONPlugin()
    out = tmp_path / "empty.json"
    plugin.export_data(out, [])

    data = json.loads(out.read_text())
    assert data == []
