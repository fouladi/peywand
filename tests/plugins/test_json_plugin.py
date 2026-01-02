import json

from pw.plugins.json_plugin import JSONPlugin


def test_json_export(tmp_path):
    plugin = JSONPlugin()

    bookmarks = [type("B", (), {"title": "T", "link": "L", "tags": "x"})()]

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
