import asyncio
import json
from pathlib import Path

from textual.widgets import DataTable, Input, Select, Static

from pw.tui import PeywandApp


def test_tui_crud_import_export_flow(tmp_path: Path) -> None:
    async def scenario() -> None:
        app = PeywandApp(tmp_path / "peywand.db")

        async with app.run_test(size=(120, 36)) as pilot:
            await pilot.pause()

            await pilot.click("#add")
            await pilot.pause()
            app.screen.query_one("#bookmark-title", Input).value = "Example"
            app.screen.query_one("#bookmark-link", Input).value = "https://example.com"
            app.screen.query_one("#bookmark-tags", Input).value = "demo;ref"
            await pilot.click("#save")
            await pilot.pause()

            table = app.query_one("#bookmarks-table", DataTable)
            assert table.row_count == 1
            assert "Example" in str(app.query_one("#details", Static).renderable)

            await pilot.click("#edit")
            await pilot.pause()
            app.screen.query_one("#bookmark-title", Input).value = "Changed"
            await pilot.click("#save")
            await pilot.pause()
            assert "Changed" in str(app.query_one("#details", Static).renderable)

            export_path = tmp_path / "bookmarks.json"
            await pilot.click("#export")
            await pilot.pause()
            app.screen.query_one("#file-format", Select).value = "json"
            app.screen.query_one("#file-path", Input).value = str(export_path)
            await pilot.click("#submit")
            await pilot.pause()

            exported = json.loads(export_path.read_text(encoding="utf-8"))
            assert exported[0]["title"] == "Changed"

            await pilot.click("#delete")
            await pilot.pause()
            await pilot.click("#confirm")
            await pilot.pause()
            assert table.row_count == 0

            await pilot.click("#import")
            await pilot.pause()
            app.screen.query_one("#file-format", Select).value = "json"
            app.screen.query_one("#file-path", Input).value = str(export_path)
            await pilot.click("#submit")
            await pilot.pause()
            assert table.row_count == 1

            app.query_one("#filter-title", Input).value = "Chang"
            await pilot.click("#apply-filters")
            await pilot.pause()
            assert table.row_count == 1

            await pilot.click("#clear-filters")
            await pilot.pause()
            assert table.row_count == 1

    asyncio.run(scenario())


def test_tui_default_size_keeps_import_export_accessible(tmp_path: Path) -> None:
    async def scenario() -> None:
        app = PeywandApp(tmp_path / "peywand.db")

        async with app.run_test() as pilot:
            await pilot.pause()

            export_path = tmp_path / "empty.json"
            await pilot.click("#export")
            await pilot.pause()
            app.screen.query_one("#file-format", Select).value = "json"
            app.screen.query_one("#file-path", Input).value = str(export_path)
            await pilot.click("#submit")
            await pilot.pause()

            assert export_path.exists()
            assert json.loads(export_path.read_text(encoding="utf-8")) == []

    asyncio.run(scenario())
