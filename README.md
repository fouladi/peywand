# Peywand

Peywand is a terminal bookmark manager built around a local SQLite
database. It now uses a Textual TUI for browsing, filtering, editing,
importing, and exporting bookmarks without relying on a browser-specific
sync flow.

The name `peywand` is Persian for `link`.

## Features

- Store bookmarks locally in `~/.pw.db`
- Browse bookmarks in a Textual table with keyboard-driven navigation
- Filter, add, update, and delete bookmarks from an interactive TUI
- Filter bookmarks by title, link, or semicolon-separated tags
- Import and export bookmarks as `html`, `json`, or `csv`
- Extend file I/O through the plugin registry in [`pw/plugins`](pw/plugins)

## Requirements

- Python `3.14+`
- `pip`

## Installation

Install the project from the repository root:

```bash
python -m pip install .
```

For local development, install it in editable mode and add the dev
tools:

```bash
python -m pip install -e .
python -m pip install -r requirements-dev.txt
```

If you prefer installing only the runtime dependencies without packaging
the project, `requirements.txt` is also available:

```bash
python -m pip install -r requirements.txt
```

## Quick Start

Launch the application:

```bash
python peywand.py
```

Launch against a custom database path:

```bash
python peywand.py --db-path ~/bookmarks.db
```

Show the version:

```bash
python peywand.py --version
```

## Commands

The Textual application supports these workflows:

- Search bookmarks by title, link, or tags from the sidebar
- Add, edit, and delete bookmarks with modal forms
- Import bookmarks from `html`, `json`, or `csv`
- Export the current filtered result set to `html`, `json`, or `csv`
- Navigate entirely from the keyboard with footer key hints

## Output Example

Listing bookmarks from the terminal:

![Peywand list output](doc/images/peywand_list.gif)

## Project Layout

- [`peywand.py`](peywand.py): launcher for the Textual app
- [`pw/tui.py`](pw/tui.py): Textual application and modal dialogs
- [`pw/services.py`](pw/services.py): reusable bookmark operations
- [`pw/`](pw): core bookmark, database, and formatting logic
- [`pw/plugins/`](pw/plugins): import/export plugins and registry
- [`tests/`](tests): unit tests

## Development

Run the test suite from the repository root:

```bash
pytest
```

Lint the codebase with Ruff:

```bash
ruff check .
```

## License

This project is licensed under the terms of the [MIT License](LICENSE).
