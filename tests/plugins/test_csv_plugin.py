import csv

from pw.plugins.csv_plugin import CSVPlugin


def test_csv_export(tmp_path):
    plugin = CSVPlugin()

    bookmarks = [
        type("B", (), {"title": "T1", "link": "L1", "tags": "a;b"})(),
        type("B", (), {"title": "T2", "link": "L2", "tags": ""})(),
    ]

    out = tmp_path / "bookmarks.csv"
    plugin.export_data(out, bookmarks)

    with out.open(encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))

    assert rows == [
        {"title": "T1", "link": "L1", "tags": "a;b"},
        {"title": "T2", "link": "L2", "tags": ""},
    ]


def test_csv_import(tmp_path, session_factory, monkeypatch):
    plugin = CSVPlugin()

    csv_file = tmp_path / "bookmarks.csv"
    csv_file.write_text(
        "title,link,tags\nTitle 1,https://a.example,a;b\nTitle 2,https://b.example,\n",
        encoding="utf-8",
    )

    inserted = []

    def fake_insert(session, bookmark):
        inserted.append(bookmark)

    monkeypatch.setattr("pw.plugins.csv_plugin.db.insert_bookmark", fake_insert)

    plugin.import_data(csv_file, session_factory)

    assert len(inserted) == 2
    assert inserted[0].title == "Title 1"
    assert inserted[1].link == "https://b.example"
