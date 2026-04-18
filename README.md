# Peywand

Peywand is a terminal bookmark manager built around a local SQLite
database. It lets you store, search, update, import, and export
bookmarks from the command line without relying on a browser-specific
sync flow.

The name `peywand` is Persian for `link`.

## Features

- Store bookmarks locally in `~/.pw.db`
- Add, list, update, and delete bookmarks from the CLI
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

Initialize the database:

```bash
python peywand.py init
```

Add a bookmark:

```bash
python peywand.py add \
  -t "Hacker News" \
  -l "https://news.ycombinator.com/" \
  -g "dev;news"
```

List all bookmarks:

```bash
python peywand.py list
```

Filter by tag:

```bash
python peywand.py list -g "dev"
```

Update a bookmark:

```bash
python peywand.py update \
  -i 1 \
  -t "Hacker News" \
  -l "https://news.ycombinator.com/" \
  -g "dev;news;reading"
```

Delete a bookmark by ID:

```bash
python peywand.py delete -i 1
```

Export bookmarks:

```bash
python peywand.py export -f json -n bookmarks.json
```

Import bookmarks:

```bash
python peywand.py import -f html -n bookmarks.html
```

Show command help:

```bash
python peywand.py -h
```

## Commands

Peywand currently supports these subcommands:

- `init`: create the SQLite database and tables
- `add`: create a bookmark with title, link, and tags
- `list`: show bookmarks, optionally filtered by title, link, or tags
- `delete`: remove bookmarks by ID or by exact title/link match
- `update`: replace the title, link, and tags of an existing bookmark
- `import`: load bookmarks from `html`, `json`, or `csv`
- `export`: write bookmarks to `html`, `json`, or `csv`
- `version`: print the current application version

## Output Example

Listing bookmarks from the terminal:

![Peywand list output](doc/images/peywand_list.gif)

## Project Layout

- [`peywand.py`](peywand.py): CLI entry point
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
