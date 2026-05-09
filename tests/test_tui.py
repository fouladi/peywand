import asyncio
import json
import time
from pathlib import Path
from threading import Event

from textual.widgets import Button, DataTable, Input, ProgressBar, Select, Static

from pw.tui import FileTransferProgressScreen, PeywandApp


async def wait_until(pilot, predicate, *, attempts: int = 40) -> None:
    for _ in range(attempts):
        await pilot.pause(0.05)
        if predicate():
            return
    raise AssertionError("Timed out waiting for condition")


def test_tui_crud_import_export_flow(tmp_path: Path) -> None:
    async def scenario() -> None:
        app = PeywandApp(tmp_path / "peywand.db")

        async with app.run_test(size=(120, 36)) as pilot:
            await pilot.pause(0.05)

            await pilot.click("#add")
            await pilot.pause(0.05)
            app.screen.query_one("#bookmark-title", Input).value = "Example"
            app.screen.query_one("#bookmark-link", Input).value = "https://example.com"
            app.screen.query_one("#bookmark-tags", Input).value = "demo;ref"
            await pilot.click("#save")
            await pilot.pause(0.05)

            table = app.query_one("#bookmarks-table", DataTable)
            assert table.row_count == 1
            assert [str(column.label) for column in table.ordered_columns] == ["Tags", "Title", "Link", "ID"]
            assert table.get_row("1") == ["demo;ref", "Example", "https://example.com", "1"]
            assert "Example" in str(app.query_one("#details", Static).renderable)

            await pilot.click("#edit")
            await pilot.pause(0.05)
            app.screen.query_one("#bookmark-title", Input).value = "Changed"
            await pilot.click("#save")
            await pilot.pause(0.05)
            assert "Changed" in str(app.query_one("#details", Static).renderable)

            export_path = tmp_path / "bookmarks.json"
            app.query_one("#export-menu", Select).value = "json"
            await pilot.pause(0.05)
            app.screen.query_one("#file-path", Input).value = str(export_path)
            app.screen.query_one("#submit", Button).press()
            await wait_until(pilot, export_path.exists)
            await wait_until(pilot, lambda: not isinstance(app.screen, FileTransferProgressScreen))

            exported = json.loads(export_path.read_text(encoding="utf-8"))
            assert exported[0]["title"] == "Changed"

            await pilot.click("#delete")
            await pilot.pause(0.05)
            await pilot.click("#confirm")
            await pilot.pause(0.05)
            assert table.row_count == 0

            app.query_one("#import-menu", Select).value = "json"
            await pilot.pause(0.05)
            app.screen.query_one("#file-path", Input).value = str(export_path)
            app.screen.query_one("#submit", Button).press()
            await wait_until(pilot, lambda: table.row_count == 1)
            assert table.row_count == 1

            app.query_one("#filter-title", Input).value = "Chang"
            await pilot.click("#apply-filters")
            await pilot.pause(0.05)
            assert table.row_count == 1

            await pilot.click("#clear-filters")
            await pilot.pause(0.05)
            assert table.row_count == 1

    asyncio.run(scenario())


def test_tui_default_size_keeps_import_export_accessible(tmp_path: Path) -> None:
    async def scenario() -> None:
        app = PeywandApp(tmp_path / "peywand.db")

        async with app.run_test() as pilot:
            await pilot.pause(0.05)

            export_path = tmp_path / "empty.json"
            app.query_one("#export-menu", Select).value = "json"
            await pilot.pause(0.05)
            app.screen.query_one("#file-path", Input).value = str(export_path)
            app.screen.query_one("#submit", Button).press()
            await wait_until(pilot, export_path.exists)
            await wait_until(pilot, lambda: not isinstance(app.screen, FileTransferProgressScreen))

            assert export_path.exists()
            assert json.loads(export_path.read_text(encoding="utf-8")) == []

    asyncio.run(scenario())


def test_tui_format_menus_reset_and_drive_file_extension(tmp_path: Path) -> None:
    async def scenario() -> None:
        app = PeywandApp(tmp_path / "peywand.db")

        async with app.run_test() as pilot:
            await pilot.pause(0.05)

            export_menu = app.query_one("#export-menu", Select)
            export_menu.value = "csv"
            await pilot.pause(0.05)
            assert export_menu.value == Select.BLANK
            assert app.screen.query_one("#file-path", Input).placeholder == "/path/to/file.csv"
            await pilot.click("#cancel")
            await pilot.pause(0.05)

            import_menu = app.query_one("#import-menu", Select)
            import_menu.value = "html"
            await pilot.pause(0.05)
            assert import_menu.value == Select.BLANK
            assert app.screen.query_one("#file-path", Input).placeholder == "/path/to/file.html"

    asyncio.run(scenario())


def test_tui_toolbar_import_export_buttons_reuse_action_menus(tmp_path: Path) -> None:
    async def scenario() -> None:
        app = PeywandApp(tmp_path / "peywand.db")

        async with app.run_test(size=(120, 36)) as pilot:
            await pilot.pause(0.05)

            await pilot.click("#toolbar-export")
            await pilot.pause(0.05)
            assert app.screen.query_one("#file-format", Select).value == "csv"
            await pilot.click("#cancel")
            await pilot.pause(0.05)

            await pilot.click("#toolbar-import")
            await pilot.pause(0.05)
            assert app.screen.query_one("#file-format", Select).value == "csv"

    asyncio.run(scenario())


def test_tui_shows_progress_modal_during_export(tmp_path: Path) -> None:
    async def scenario() -> None:
        app = PeywandApp(tmp_path / "peywand.db")
        release_export = Event()

        def slow_export_bookmarks(*, path: Path, file_format: str, filters=None, progress_callback=None) -> None:
            if progress_callback is not None:
                progress_callback(0, 3)
            release_export.wait(timeout=1)
            for completed in range(1, 4):
                if progress_callback is not None:
                    progress_callback(completed, 3)
                time.sleep(0.01)
            path.write_text("[]", encoding="utf-8")

        async with app.run_test(size=(120, 36)) as pilot:
            await pilot.pause(0.05)
            app.service.export_bookmarks = slow_export_bookmarks

            export_path = tmp_path / "slow.json"
            app.query_one("#export-menu", Select).value = "json"
            await pilot.pause(0.05)
            app.screen.query_one("#file-path", Input).value = str(export_path)
            app.screen.query_one("#submit", Button).press()
            await wait_until(pilot, lambda: isinstance(app.screen, FileTransferProgressScreen))

            progress_screen = app.screen
            assert isinstance(progress_screen, FileTransferProgressScreen)
            progress_bar = progress_screen.query_one("#transfer-progress", ProgressBar)
            assert progress_bar.total == 3
            assert progress_bar.progress == 0
            assert str(progress_screen.query_one("#progress-status", Static).renderable) == "0 of 3 bookmarks"

            release_export.set()
            await wait_until(pilot, export_path.exists)
            await wait_until(pilot, lambda: not isinstance(app.screen, FileTransferProgressScreen))

    asyncio.run(scenario())
