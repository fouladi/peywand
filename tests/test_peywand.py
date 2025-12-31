from collections.abc import Generator

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from pw import bookmark_view, db
from pw.bookmark import Bookmark
from pw.models import Base


@pytest.fixture
def session() -> Generator[Session]:
    """Provide a SQLAlchemy session backed by in-memory SQLite."""

    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)

    SessionLocal = sessionmaker(engine, expire_on_commit=False)

    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
        engine.dispose()


def test_all(session: Session) -> None:
    b1 = Bookmark(None, "hallo1", "somewhere1/else", "dev;test")
    b2 = Bookmark(None, "hallo2", "somewhere2/else", "dev")
    b3 = Bookmark(None, "hallo3", "somewhere3/else", "test")
    b4 = Bookmark(None, "hallo4", "somewhere4/else", "dev;test")
    b5 = Bookmark(None, "hallo5", "somewhere5/else", "test")
    b6 = Bookmark(None, "hallo6", "somewhere6/else", "dev;test")
    b7 = Bookmark(None, "hallo7", "somewhere7/else", "dev;test")

    db.insert_bookmark(session, b1)
    db.insert_bookmark(session, b2)
    db.insert_bookmark(session, b3)
    db.insert_bookmark(session, b4)
    db.insert_bookmark(session, b5)
    db.insert_bookmark(session, b6)
    db.insert_bookmark(session, b7)

    b8 = db.get_bookmark_by_id(session, 5)
    assert b8.title == b5.title

    bookmark_view.print_search_result([b1, b2, b3, b4, b5, b6, b7, b8], alternate_row_color="no")
    bookmark_view.print_search_result([], alternate_row_color="no")

    books = db.get_bookmarks_by_title(session)
    bookmark_view.print_search_result(books, alternate_row_color="light_green")

    b11 = Bookmark(None, "hallo", "farrrrrr", "dad;baba")
    db.update_bookmark(session, 3, b11)

    b3_new = db.get_bookmark_by_id(session, 3)
    assert b3_new.title == b11.title

    b12 = db.get_bookmarks_by_title(session)
    bookmark_view.print_search_result(b12, alternate_row_color="light_green")
