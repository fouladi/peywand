from sqlalchemy import (
    create_engine,
    delete,
    event,
    select,
)
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from .bookmark import Bookmark
from .models import Base, Bookmarks, Tags


def create_engine_and_session(db_path: str) -> sessionmaker[Session]:
    """“Database is created automatically when the engine/session is created.”"""
    engine = create_engine(f"sqlite:///{db_path}", future=True)
    Base.metadata.create_all(engine)
    return sessionmaker(engine, expire_on_commit=False)


@event.listens_for(Engine, "connect")
def enable_sqlite_foreign_keys(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


def create_database(db_path: str) -> None:
    """Create an empty SQLite database and all tables defined

    by the SQLAlchemy ORM models.
    """
    engine = create_engine(f"sqlite:///{db_path}", future=True)
    Base.metadata.create_all(engine)


def _split_tags(tags: str) -> list[str]:
    return list({t for t in tags.split(";") if t})


def get_bookmark_by_id(session: Session, bookmark_id: int) -> Bookmark:
    bookmark = session.get(Bookmarks, bookmark_id)
    if not bookmark:
        raise ValueError(f"Bookmark with id={bookmark_id} not found.")
    return bookmark.to_dataclass()


def get_bookmarks_by_title(
    session: Session,
    query_string: str = "",
    is_strict: bool = False,
) -> list[Bookmark]:
    pattern = query_string if is_strict else f"%{query_string}%"

    stmt = select(Bookmarks).where(Bookmarks.title.ilike(pattern))
    return [b.to_dataclass() for b in session.scalars(stmt)]


def get_bookmarks_by_link(
    session: Session,
    query_string: str = "",
    is_strict: bool = False,
) -> list[Bookmark]:
    pattern = query_string if is_strict else f"%{query_string}%"

    stmt = select(Bookmarks).where(Bookmarks.link.ilike(pattern))
    return [b.to_dataclass() for b in session.scalars(stmt)]


def get_bookmarks_by_tags(
    session: Session,
    tags: list[str],
    is_strict: bool = False,
) -> list[Bookmark]:
    if not tags:
        return []

    conditions = []
    for tag in tags:
        pattern = tag if is_strict else f"%{tag}%"
        conditions.append(Tags.tag.ilike(pattern))

    stmt = select(Bookmarks).join(Tags).where(*conditions).distinct()

    return [b.to_dataclass() for b in session.scalars(stmt)]


def get_bookmarks_by_filter(
    session: Session,
    title: str | None = None,
    link: str | None = None,
    tags: list[str] | None = None,
    is_strict: bool = False,
) -> list[Bookmark] | None:
    stmt = select(Bookmarks)

    if title is not None:
        pattern = title if is_strict else f"%{title}%"
        stmt = stmt.where(Bookmarks.title.ilike(pattern))

    if link is not None:
        pattern = link if is_strict else f"%{link}%"
        stmt = stmt.where(Bookmarks.link.ilike(pattern))

    if tags:
        stmt = stmt.join(Tags)
        for tag in tags:
            pattern = tag if is_strict else f"%{tag}%"
            stmt = stmt.where(Tags.tag.ilike(pattern))

    result = list(session.scalars(stmt.distinct()))
    return [b.to_dataclass() for b in result] if result else None


def get_uniq_bookmark_by_filter(
    session: Session,
    **kwargs,
) -> Bookmark | None:
    bookmarks = get_bookmarks_by_filter(session, **kwargs)
    return bookmarks[0] if bookmarks and len(bookmarks) == 1 else None


def insert_bookmark(session: Session, bookmark: Bookmark) -> None:
    exists = session.scalar(select(Bookmarks).where(Bookmarks.link == bookmark.link))
    if exists:
        raise ValueError(f"Bookmark with link '{bookmark.link}' already exists!")

    orm = Bookmarks(
        title=bookmark.title,
        link=bookmark.link,
        tags=bookmark.tags,
        tag_items=[Tags(tag=t) for t in _split_tags(bookmark.tags)],
    )

    session.add(orm)
    session.commit()


def delete_bookmark_by_id(session: Session, bookmark_id: int) -> None:
    session.execute(delete(Bookmarks).where(Bookmarks.id == bookmark_id))
    session.commit()


def delete_bookmark_by_name(session: Session, title: str, link: str) -> None:
    session.execute(delete(Bookmarks).where(Bookmarks.title == title).where(Bookmarks.link == link))
    session.commit()


def update_bookmark(session: Session, bookmark_id: int, bookmark: Bookmark) -> None:
    orm = session.get(Bookmarks, bookmark_id)
    if not orm:
        raise ValueError("Bookmark not found")

    orm.title = bookmark.title
    orm.link = bookmark.link
    orm.tags = bookmark.tags
    orm.tag_items = [Tags(tag=t) for t in _split_tags(bookmark.tags)]

    session.commit()
