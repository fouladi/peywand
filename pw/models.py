from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from .bookmark import Bookmark


class Base(DeclarativeBase):
    pass


class Bookmarks(Base):
    __tablename__ = "bookmarks"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    link: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    tags: Mapped[str | None] = mapped_column(String)

    tag_items: Mapped[list[Tags]] = relationship(
        back_populates="bookmark",
        cascade="all, delete-orphan",
    )

    def to_dataclass(self) -> Bookmark:
        return Bookmark(
            id=self.id,
            title=self.title,
            link=self.link,
            tags=self.tags or "",
        )


class Tags(Base):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(primary_key=True)
    bookmark_id: Mapped[int] = mapped_column(ForeignKey("bookmarks.id", ondelete="CASCADE"))
    tag: Mapped[str] = mapped_column(String, nullable=False)

    bookmark: Mapped[Bookmarks] = relationship(back_populates="tag_items")
