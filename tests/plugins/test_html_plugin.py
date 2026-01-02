from pw.plugins.html_plugin import HTMLPlugin


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
