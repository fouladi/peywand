from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class Bookmark:
    id: int | None
    title: str
    link: str
    tags: str
