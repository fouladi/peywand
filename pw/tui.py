from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Grid, Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, DataTable, Footer, Header, Input, Label, Select, Static

from pw.bookmark import Bookmark
from pw.services import BookmarkFilters, BookmarkService


@dataclass(slots=True, frozen=True)
class BookmarkFormData:
    title: str
    link: str
    tags: str


@dataclass(slots=True, frozen=True)
class FileActionData:
    file_format: str
    path: str


class ConfirmScreen(ModalScreen[bool]):
    BINDINGS = [Binding("escape", "cancel", "Cancel")]

    def __init__(self, question: str) -> None:
        super().__init__()
        self.question = question

    def compose(self) -> ComposeResult:
        with Grid(id="modal-dialog", classes="confirm-dialog"):
            yield Label(self.question, id="modal-title")
            yield Button("Delete", id="confirm", variant="error")
            yield Button("Cancel", id="cancel", variant="primary")

    def action_cancel(self) -> None:
        self.dismiss(False)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.dismiss(event.button.id == "confirm")


class BookmarkFormScreen(ModalScreen[BookmarkFormData | None]):
    BINDINGS = [Binding("escape", "cancel", "Cancel")]

    def __init__(self, title: str, bookmark: Bookmark | None = None) -> None:
        super().__init__()
        self.screen_title = title
        self.bookmark = bookmark

    def compose(self) -> ComposeResult:
        with Grid(id="modal-dialog", classes="bookmark-form"):
            yield Label(self.screen_title, id="modal-title")
            yield Input(value=self.bookmark.title if self.bookmark else "", placeholder="Title", id="bookmark-title")
            yield Input(value=self.bookmark.link if self.bookmark else "", placeholder="Link", id="bookmark-link")
            yield Input(
                value=self.bookmark.tags if self.bookmark else "", placeholder="Tags: dev;news", id="bookmark-tags"
            )
            with Horizontal(classes="dialog-buttons"):
                yield Button("Save", id="save", variant="success")
                yield Button("Cancel", id="cancel", variant="primary")

    def on_mount(self) -> None:
        self.query_one("#bookmark-title", Input).focus()

    def action_cancel(self) -> None:
        self.dismiss(None)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "cancel":
            self.dismiss(None)
            return

        title = self.query_one("#bookmark-title", Input).value.strip()
        link = self.query_one("#bookmark-link", Input).value.strip()
        tags = self.query_one("#bookmark-tags", Input).value.strip()

        if not title or not link:
            self.notify("Title and link are required.", severity="error")
            return

        self.dismiss(BookmarkFormData(title=title, link=link, tags=tags))


class FileActionScreen(ModalScreen[FileActionData | None]):
    BINDINGS = [Binding("escape", "cancel", "Cancel")]

    def __init__(self, title: str, formats: list[str], default_path: str = "") -> None:
        super().__init__()
        self.screen_title = title
        self.formats = formats
        self.default_path = default_path

    def compose(self) -> ComposeResult:
        options = [(file_format.upper(), file_format) for file_format in self.formats]
        default_format = self.formats[0]

        with Grid(id="modal-dialog", classes="file-form"):
            yield Label(self.screen_title, id="modal-title")
            yield Select(options, allow_blank=False, value=default_format, id="file-format")
            yield Input(value=self.default_path, placeholder="/path/to/file.json", id="file-path")
            with Horizontal(classes="dialog-buttons"):
                yield Button("Run", id="submit", variant="success")
                yield Button("Cancel", id="cancel", variant="primary")

    def on_mount(self) -> None:
        self.query_one("#file-path", Input).focus()

    def action_cancel(self) -> None:
        self.dismiss(None)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "cancel":
            self.dismiss(None)
            return

        file_format = str(self.query_one("#file-format", Select).value)
        path = self.query_one("#file-path", Input).value.strip()

        if not path:
            self.notify("A file path is required.", severity="error")
            return

        self.dismiss(FileActionData(file_format=file_format, path=path))


class PeywandApp(App[None]):
    CSS_PATH = "tui.tcss"
    TITLE = "Peywand"
    SUB_TITLE = "Bookmark manager"
    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("r", "refresh", "Refresh"),
        Binding("a", "add_bookmark", "Add"),
        Binding("e", "edit_bookmark", "Edit"),
        Binding("d", "delete_bookmark", "Delete"),
        Binding("i", "import_bookmarks", "Import"),
        Binding("x", "export_bookmarks", "Export"),
    ]

    def __init__(self, db_path: Path) -> None:
        super().__init__()
        self.service = BookmarkService(db_path)
        self.bookmarks: list[Bookmark] = []
        self.selected_bookmark_id: int | None = None

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Horizontal(id="app-shell"):
            with Vertical(id="sidebar"):
                yield Static("Find", classes="panel-title")
                yield Input(placeholder="Title contains...", id="filter-title")
                yield Input(placeholder="Link contains...", id="filter-link")
                yield Input(placeholder="Tags: dev;news", id="filter-tags")
                with Horizontal(classes="sidebar-actions"):
                    yield Button("Apply", id="apply-filters", variant="primary")
                    yield Button("Clear", id="clear-filters")
                with Horizontal(classes="sidebar-actions"):
                    yield Button("Import", id="import")
                    yield Button("Export", id="export")
                yield Static("", id="stats", classes="panel-block")
                yield Static("No bookmark selected.", id="details", classes="panel-block")
            with Vertical(id="main-pane"):
                yield Static("Bookmarks", classes="panel-title")
                with Horizontal(id="toolbar"):
                    yield Button("Add", id="add", variant="success", compact=True)
                    yield Button("Edit", id="edit", compact=True)
                    yield Button("Delete", id="delete", variant="error", compact=True)
                yield DataTable(id="bookmarks-table", zebra_stripes=True, cursor_type="row")
        yield Footer()

    def on_mount(self) -> None:
        self.service.initialize_database()
        table = self.query_one("#bookmarks-table", DataTable)
        table.add_columns("ID", "Title", "Link", "Tags")
        table.focus()
        self.refresh_table()

    def on_unmount(self) -> None:
        self.service.close()

    def current_filters(self) -> BookmarkFilters:
        return BookmarkFilters(
            title=self.query_one("#filter-title", Input).value.strip(),
            link=self.query_one("#filter-link", Input).value.strip(),
            tags=self.query_one("#filter-tags", Input).value.strip(),
        )

    def selected_bookmark(self) -> Bookmark | None:
        if self.selected_bookmark_id is None:
            return None
        return next((bookmark for bookmark in self.bookmarks if bookmark.id == self.selected_bookmark_id), None)

    def _bookmark_id_from_row_key(self, row_key: object) -> int:
        value = getattr(row_key, "value", row_key)
        return int(str(value))

    def refresh_table(self, preferred_bookmark_id: int | None = None) -> None:
        table = self.query_one("#bookmarks-table", DataTable)
        self.bookmarks = self.service.list_bookmarks(self.current_filters())
        table.clear()

        for bookmark in self.bookmarks:
            table.add_row(
                str(bookmark.id or ""),
                bookmark.title,
                bookmark.link,
                bookmark.tags,
                key=str(bookmark.id),
            )

        if self.bookmarks:
            selected_index = 0
            if preferred_bookmark_id is not None:
                selected_index = next(
                    (index for index, bookmark in enumerate(self.bookmarks) if bookmark.id == preferred_bookmark_id),
                    0,
                )
            self.selected_bookmark_id = self.bookmarks[selected_index].id
            table.move_cursor(row=selected_index, column=0)
        else:
            self.selected_bookmark_id = None

        self.refresh_sidebar()

    def refresh_sidebar(self) -> None:
        stats = self.query_one("#stats", Static)
        bookmark = self.selected_bookmark()
        stats.update(f"{len(self.bookmarks)} bookmark(s) loaded")

        if bookmark is None:
            self.query_one("#details", Static).update("No bookmark selected.")
            return

        details = "\n".join(
            [
                f"ID: {bookmark.id}",
                f"Title: {bookmark.title}",
                f"Link: {bookmark.link}",
                f"Tags: {bookmark.tags or '-'}",
            ]
        )
        self.query_one("#details", Static).update(details)

    def action_refresh(self) -> None:
        self.refresh_table()
        self.notify("Bookmarks refreshed.")

    def action_add_bookmark(self) -> None:
        self.push_screen(BookmarkFormScreen("Add bookmark"), self._handle_add_result)

    def action_edit_bookmark(self) -> None:
        bookmark = self.selected_bookmark()
        if bookmark is None:
            self.notify("Select a bookmark first.", severity="warning")
            return

        self.push_screen(BookmarkFormScreen("Edit bookmark", bookmark), self._handle_edit_result)

    def action_delete_bookmark(self) -> None:
        bookmark = self.selected_bookmark()
        if bookmark is None:
            self.notify("Select a bookmark first.", severity="warning")
            return

        self.push_screen(ConfirmScreen(f"Delete '{bookmark.title}'?"), self._handle_delete_result)

    def action_import_bookmarks(self) -> None:
        self.push_screen(
            FileActionScreen("Import bookmarks", self.service.available_formats()),
            self._handle_import_result,
        )

    def action_export_bookmarks(self) -> None:
        self.push_screen(
            FileActionScreen("Export current results", self.service.available_formats()),
            self._handle_export_result,
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id
        if button_id == "apply-filters":
            self.refresh_table()
        elif button_id == "clear-filters":
            for widget_id in ("#filter-title", "#filter-link", "#filter-tags"):
                self.query_one(widget_id, Input).value = ""
            self.refresh_table()
        elif button_id == "add":
            self.action_add_bookmark()
        elif button_id == "edit":
            self.action_edit_bookmark()
        elif button_id == "delete":
            self.action_delete_bookmark()
        elif button_id == "import":
            self.action_import_bookmarks()
        elif button_id == "export":
            self.action_export_bookmarks()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id in {"filter-title", "filter-link", "filter-tags"}:
            self.refresh_table()

    def on_data_table_row_highlighted(self, event: DataTable.RowHighlighted) -> None:
        self.selected_bookmark_id = self._bookmark_id_from_row_key(event.row_key)
        self.refresh_sidebar()

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        self.selected_bookmark_id = self._bookmark_id_from_row_key(event.row_key)
        self.refresh_sidebar()

    def _handle_add_result(self, result: BookmarkFormData | None) -> None:
        if result is None:
            return

        try:
            bookmark = self.service.add_bookmark(title=result.title, link=result.link, tags=result.tags)
        except (SystemExit, ValueError) as error:
            self.notify(str(error), severity="error", timeout=8)
            return

        self.refresh_table(preferred_bookmark_id=bookmark.id)
        self.notify(f"Added '{bookmark.title}'.")

    def _handle_edit_result(self, result: BookmarkFormData | None) -> None:
        bookmark = self.selected_bookmark()
        if result is None or bookmark is None or bookmark.id is None:
            return

        try:
            updated = self.service.update_bookmark(
                bookmark.id,
                title=result.title,
                link=result.link,
                tags=result.tags,
            )
        except ValueError as error:
            self.notify(str(error), severity="error", timeout=8)
            return

        self.refresh_table(preferred_bookmark_id=updated.id)
        self.notify(f"Updated '{updated.title}'.")

    def _handle_delete_result(self, confirmed: bool) -> None:
        bookmark = self.selected_bookmark()
        if not confirmed or bookmark is None or bookmark.id is None:
            return

        self.service.delete_bookmark(bookmark.id)
        self.refresh_table()
        self.notify(f"Deleted '{bookmark.title}'.")

    def _handle_import_result(self, result: FileActionData | None) -> None:
        if result is None:
            return

        try:
            self.service.import_bookmarks(path=Path(result.path).expanduser(), file_format=result.file_format)
        except (OSError, ValueError, SystemExit) as error:
            self.notify(str(error), severity="error", timeout=8)
            return

        self.refresh_table()
        self.notify(f"Imported bookmarks from {result.path}.")

    def _handle_export_result(self, result: FileActionData | None) -> None:
        if result is None:
            return

        try:
            self.service.export_bookmarks(
                path=Path(result.path).expanduser(),
                file_format=result.file_format,
                filters=self.current_filters(),
            )
        except (OSError, ValueError) as error:
            self.notify(str(error), severity="error", timeout=8)
            return

        self.notify(f"Exported bookmarks to {result.path}.")
