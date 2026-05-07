"""Tests for pw/db.py — covers previously uncovered lines:

- create_database (line 62)
- get_bookmarks_by_link (lines 100-103)
- get_bookmarks_by_tags (lines 120-130)
- get_bookmarks_by_filter strict mode (line 195)
- delete_bookmark_by_name (lines 227-228)
- update_bookmark not-found error (line 245)
"""

from collections.abc import Generator
from pathlib import Path

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from pw import db
from pw.bookmark import Bookmark
from pw.models import Base

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def session() -> Generator[Session]:
    """In-memory SQLite session for fast, isolated tests."""
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(engine, expire_on_commit=False)
    s = SessionLocal()
    try:
        yield s
    finally:
        s.close()
        engine.dispose()


def _insert(session: Session, title: str, link: str, tags: str = "") -> Bookmark:
    """Helper: insert a bookmark and return it."""
    bm = Bookmark(id=None, title=title, link=link, tags=tags)
    db.insert_bookmark(session, bm)
    return bm


# ---------------------------------------------------------------------------
# create_database
# ---------------------------------------------------------------------------


def test_create_database_is_idempotent(tmp_path: Path) -> None:
    """create_database can be called multiple times without error."""
    db_path = str(tmp_path / "test.db")
    db.create_database(db_path)
    db.create_database(db_path)  # second call must not raise


# ---------------------------------------------------------------------------
# get_bookmarks_by_link
# ---------------------------------------------------------------------------


def test_get_bookmarks_by_link_fuzzy(session: Session) -> None:
    _insert(session, "Python", "https://python.org", "lang")
    _insert(session, "GitHub", "https://github.com", "dev")

    results = db.get_bookmarks_by_link(session, "python")
    assert len(results) == 1
    assert results[0].link == "https://python.org"


def test_get_bookmarks_by_link_strict(session: Session) -> None:
    _insert(session, "Python", "https://python.org", "lang")

    # Strict match — exact URL
    results = db.get_bookmarks_by_link(session, "https://python.org", is_strict=True)
    assert len(results) == 1

    # Strict match — partial URL should return nothing
    results = db.get_bookmarks_by_link(session, "python.org", is_strict=True)
    assert results == []


def test_get_bookmarks_by_link_no_match(session: Session) -> None:
    _insert(session, "Python", "https://python.org")

    results = db.get_bookmarks_by_link(session, "notexist")
    assert results == []


# ---------------------------------------------------------------------------
# get_bookmarks_by_tags
# ---------------------------------------------------------------------------


def test_get_bookmarks_by_tags_fuzzy(session: Session) -> None:
    _insert(session, "Python", "https://python.org", "lang;docs")
    _insert(session, "GitHub", "https://github.com", "dev;tools")

    results = db.get_bookmarks_by_tags(session, ["lang"])
    assert len(results) == 1
    assert results[0].title == "Python"


def test_get_bookmarks_by_tags_strict(session: Session) -> None:
    _insert(session, "Python", "https://python.org", "lang;docs")

    results = db.get_bookmarks_by_tags(session, ["lang"], is_strict=True)
    assert len(results) == 1

    # "lan" is not an exact tag
    results = db.get_bookmarks_by_tags(session, ["lan"], is_strict=True)
    assert results == []


def test_get_bookmarks_by_tags_empty_list(session: Session) -> None:
    _insert(session, "Python", "https://python.org", "lang")

    results = db.get_bookmarks_by_tags(session, [])
    assert results == []


def test_get_bookmarks_by_tags_multiple(session: Session) -> None:
    """Multiple tags in the list are combined with AND — a single tag row must match all patterns.

    This means the current implementation only works when searching for a single tag.
    For multiple tags, the query returns empty because no single tag row can match
    multiple different patterns simultaneously.
    """
    _insert(session, "Python", "https://python.org", "lang;docs")
    _insert(session, "GitHub", "https://github.com", "dev;tools")

    # Single tag works fine
    results = db.get_bookmarks_by_tags(session, ["lang"])
    assert len(results) == 1
    assert results[0].title == "Python"

    # Multiple tags with AND semantics — current implementation limitation
    # (would need a subquery or group-by-having to work correctly)
    results = db.get_bookmarks_by_tags(session, ["lang", "docs"])
    assert results == []  # no single tag row matches both patterns


# ---------------------------------------------------------------------------
# get_bookmarks_by_filter — strict mode
# ---------------------------------------------------------------------------


def test_get_bookmarks_by_filter_strict_title(session: Session) -> None:
    _insert(session, "Python", "https://python.org", "lang")
    _insert(session, "Python Docs", "https://docs.python.org", "docs")

    # Strict: only exact title match
    results = db.get_bookmarks_by_filter(session, title="Python", is_strict=True)
    assert len(results) == 1
    assert results[0].title == "Python"


def test_get_bookmarks_by_filter_strict_link(session: Session) -> None:
    _insert(session, "Python", "https://python.org")

    results = db.get_bookmarks_by_filter(session, link="https://python.org", is_strict=True)
    assert len(results) == 1

    results = db.get_bookmarks_by_filter(session, link="python.org", is_strict=True)
    assert results == []


def test_get_bookmarks_by_filter_strict_tags(session: Session) -> None:
    _insert(session, "Python", "https://python.org", "lang;docs")

    results = db.get_bookmarks_by_filter(session, tags=["lang"], is_strict=True)
    assert len(results) == 1

    results = db.get_bookmarks_by_filter(session, tags=["la"], is_strict=True)
    assert results == []


# ---------------------------------------------------------------------------
# delete_bookmark_by_name
# ---------------------------------------------------------------------------


def test_delete_bookmark_by_name(session: Session) -> None:
    _insert(session, "Python", "https://python.org", "lang")

    db.delete_bookmark_by_name(session, "Python", "https://python.org")

    results = db.get_bookmarks_by_title(session)
    assert results == []


def test_delete_bookmark_by_name_no_match_is_safe(session: Session) -> None:
    """Deleting a non-existent bookmark by name should not raise."""
    _insert(session, "Python", "https://python.org")

    db.delete_bookmark_by_name(session, "DoesNotExist", "https://nowhere.com")

    results = db.get_bookmarks_by_title(session)
    assert len(results) == 1


# ---------------------------------------------------------------------------
# update_bookmark — not-found error
# ---------------------------------------------------------------------------


def test_update_bookmark_not_found_raises(session: Session) -> None:
    with pytest.raises(ValueError, match="Bookmark not found"):
        db.update_bookmark(session, 9999, Bookmark(id=None, title="X", link="https://x.com", tags=""))
