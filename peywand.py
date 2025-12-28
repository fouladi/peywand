#!/usr/bin/env python3
import re
from pathlib import Path

from tqdm import tqdm

from pw import __version__ as pw_version, db, search
from pw.bookmark import Bookmark
from pw.util import argpars

DB_PATH = Path.home() / ".pw.db"
REG_TITLE = re.compile(r"^>(.*?)<")

SessionLocal = db.create_engine_and_session(str(DB_PATH))


def ensure_rows(rows: list[Bookmark] | None) -> list[Bookmark]:
    """Ensure a non-None list of bookmarks."""
    return rows or []


def handle_init() -> None:
    db.create_database(str(DB_PATH))
    print(f"Database initialized at {DB_PATH}")


def handle_add() -> None:
    bookmark = Bookmark(
        id=None,
        title=argpars.title,
        link=argpars.link,
        tags=argpars.tags,
    )

    with SessionLocal() as session:
        db.insert_bookmark(session, bookmark)


def handle_list() -> None:
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
    color_mode = not argpars.no_color
    search.print_search_result(bookmarks, color_mode)


def handle_delete() -> None:
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
    print(f"Current version: {pw_version}")


def handle_default() -> None:
    print("\t\tUsage: ./peywand.py -h\n")


def main() -> None:
    """Main program entry point for Peywand bookmark manager."""
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
