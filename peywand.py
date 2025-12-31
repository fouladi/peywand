#!/usr/bin/env python3
import re
from pathlib import Path

from tqdm import tqdm

from pw import __version__ as pw_version, db
from pw.bookmark import Bookmark
from pw.bookmark_view import print_search_result
from pw.util import argpars

DB_PATH = Path.home() / ".pw.db"
REG_TITLE = re.compile(r"^>(.*?)<")

SessionLocal = db.create_engine_and_session(str(DB_PATH))


def ensure_rows(rows: list[Bookmark] | None) -> list[Bookmark]:
    """Ensure a non-None list of bookmarks."""
    return rows or []


def handle_init() -> None:
    """Initialize the Peywand database.

    Creates the SQLite database file (if it does not exist) and
    initializes all required tables using SQLAlchemy metadata.
    """
    db.create_database(str(DB_PATH))
    print(f"Database initialized at {DB_PATH}")


def handle_add() -> None:
    """Add a new bookmark to the database.

    Reads title, link, and tags from CLI arguments and inserts
    a new bookmark into the database.

    Raises:
        SystemExit: If a bookmark with the same link already exists.
    """
    bookmark = Bookmark(
        id=None,
        title=argpars.title,
        link=argpars.link,
        tags=argpars.tags,
    )

    with SessionLocal() as session:
        db.insert_bookmark(session, bookmark)


def handle_list() -> None:
    """List bookmarks from the database.

    Supports optional filtering by:
    - title
    - link
    - tags

    Results are sorted alphabetically by title and printed
    using the search output formatter.
    """
    tags_list: list[str] | None = None
    if argpars.tags:
        tags_list = argpars.tags.split(";")

    with SessionLocal() as session:
        if argpars.title or argpars.link or tags_list:
            rows = db.get_bookmarks_by_filter(
                session,
                title=argpars.title,
                link=argpars.link,
                tags=tags_list,
            )
        else:
            rows = db.get_bookmarks_by_title(session)

    bookmarks = sorted(ensure_rows(rows), key=lambda b: b.title)
    print_search_result(bookmarks, alternate_row_color=argpars.row_bg_color)


def handle_delete() -> None:
    """Delete bookmarks from the database.

    Deletion can be performed by:
    - Bookmark ID (preferred, unambiguous)
    - Title and link (strict match)

    If multiple bookmarks match a non-ID query, deletion is aborted
    and the user is asked to provide a more specific identifier.
    """
    with SessionLocal() as session:
        if argpars.id:
            for id_str in argpars.id:
                bookmark_id = int(id_str)
                bookmark = db.get_bookmark_by_id(session, bookmark_id)
                if bookmark.id is not None:
                    db.delete_bookmark_by_id(session, bookmark.id)
                    print(f"Bookmark '{bookmark.link}/{bookmark.title}' removed!")
                else:
                    print(f"Bookmark with ID {bookmark_id} not found.")
            return

        if argpars.title:
            bookmarks = db.get_bookmarks_by_filter(
                session,
                title=argpars.title,
                link=argpars.link,
                is_strict=True,
            )
            if bookmarks and len(bookmarks) == 1:
                bookmark = bookmarks[0]
                if bookmark.id is not None:
                    db.delete_bookmark_by_id(session, bookmark.id)
                    print(f"Bookmark '{bookmark.link}/{bookmark.title}' removed!")
            else:
                print("There is more than one bookmark with that title, please specify a correct link!")


def handle_update() -> None:
    """Update an existing bookmark.

    Updates the title, link, and tags of a bookmark identified
    by its unique ID.

    If no ID is provided, the update operation is aborted.
    """
    if argpars.id is None:
        print("Missing bookmark ID for update.")
        return

    bookmark = Bookmark(
        id=None,
        title=argpars.title,
        link=argpars.link,
        tags=argpars.tags,
    )

    with SessionLocal() as session:
        db.update_bookmark(session, argpars.id, bookmark)

    print(f"Bookmark '{bookmark.link}/{bookmark.title}' updated!")


def handle_import() -> None:
    """Import bookmarks from an HTML-like file.

    Reads bookmark entries line by line, extracts title, link, and tags,
    and inserts them into the database. The format a read line is like:

    <li title="admin"><a href="https://statuses.now.sh/">HTTP Status</a></li>

    A progress bar is displayed to indicate import progress.
    Duplicate bookmarks are skipped.
    """
    if not argpars.file_name:
        print("Missing import file name.")
        return

    file_path = Path(argpars.file_name)
    if not file_path.exists():
        print(f"File not found: {file_path}")
        return

    # Count total lines for progress bar
    with file_path.open("r", encoding="utf-8") as fh:
        total_lines = sum(1 for _ in fh)

    with (
        SessionLocal() as session,
        file_path.open("r", encoding="utf-8") as fh,
        tqdm(total=total_lines, desc="Importing bookmarks", unit="lines") as bar,
    ):
        for line in fh:
            bar.update(1)

            parts = line.split('"')
            if len(parts) < 5:
                continue

            tags = parts[1]
            link = parts[3]
            match = re.search(REG_TITLE, parts[4])
            if not match:
                continue

            title = match.group(1)
            bookmark = Bookmark(id=None, title=title, link=link, tags=tags)

            try:
                db.insert_bookmark(session, bookmark)
            except ValueError:
                # Duplicate links or invalid entries
                continue


def handle_export() -> None:
    """Export bookmarks to an HTML-like file.

    Writes all bookmarks to the specified output file in a format
    compatible with browser bookmark imports. The format of a written
    line is like:

    <li title="admin"><a href="https://statuses.now.sh/">HTTP Status</a></li>

    A progress bar is displayed during export.
    """
    if not argpars.file_name:
        print("Missing export file name.")
        return

    file_path = Path(argpars.file_name)

    with SessionLocal() as session:
        bookmarks = ensure_rows(db.get_bookmarks_by_filter(session, title=""))

    total = len(bookmarks)

    with (
        file_path.open("w", encoding="utf-8") as fh,
        tqdm(total=total, desc="Exporting bookmarks", unit="bookmarks") as bar,
    ):
        for book in bookmarks:
            tags = book.tags.replace(";", ",") if book.tags else ""
            fh.write(f'<li title="{tags}"><a href="{book.link}">{book.title}</a></li>\n')
            bar.update(1)


def handle_version() -> None:
    """Print the current Peywand application version."""
    print(f"Current version: {pw_version}")


def handle_default() -> None:
    """Display usage instructions for the Peywand CLI.

    This function is called when no valid command is provided.
    """
    print("\t\tUsage: ./peywand.py -h\n")


def main() -> None:
    """Main entry point for the Peywand CLI application.

    Dispatches the parsed command to the appropriate handler function
    based on CLI arguments.
    """
    match argpars.command:
        case "init":
            handle_init()
        case "add":
            handle_add()
        case "list":
            handle_list()
        case "delete":
            handle_delete()
        case "update":
            handle_update()
        case "import":
            handle_import()
        case "export":
            handle_export()
        case "version":
            handle_version()
        case _:
            handle_default()


if __name__ == "__main__":
    main()
