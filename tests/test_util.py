"""Tests for pw/util.py — covers previously uncovered lines 10-24:

- build_launcher_parser() default db-path
- build_launcher_parser() --db-path override
- build_launcher_parser() --version flag
"""

from pathlib import Path

from pw.util import DEFAULT_BG_COLOR, build_launcher_parser


def test_default_db_path() -> None:
    """Default --db-path should point to ~/.pw.db."""
    parser = build_launcher_parser()
    args = parser.parse_args([])

    assert args.db_path == str(Path.home() / ".pw.db")
    assert args.version is False


def test_custom_db_path() -> None:
    parser = build_launcher_parser()
    args = parser.parse_args(["--db-path", "/tmp/custom.db"])

    assert args.db_path == "/tmp/custom.db"


def test_version_flag() -> None:
    parser = build_launcher_parser()
    args = parser.parse_args(["--version"])

    assert args.version is True


def test_default_bg_color_is_defined() -> None:
    assert DEFAULT_BG_COLOR == "#303030"
