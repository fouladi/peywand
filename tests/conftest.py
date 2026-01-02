from collections import namedtuple
from pathlib import Path

import pytest

Bookmark = namedtuple("Bookmark", "id title link tags")


@pytest.fixture
def tmp_file(tmp_path: Path) -> Path:
    return tmp_path / "data.tmp"


@pytest.fixture
def fake_session():
    class FakeSession:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

    return FakeSession()


@pytest.fixture
def session_factory(fake_session):
    def factory():
        return fake_session

    return factory
