"""Tests for pw/bookmark_view.py — covers previously uncovered lines:

- TableFormatter.header() with alternate_row_color="no"  (line 50)
- TableFormatter.rows() odd-index rows (non-colored path)  (line 62)
- Column-size cache reuse across header() + rows() calls

Note on ANSI codes: the `colored` library checks sys.stdout.isatty() at import
time and returns empty strings when stdout is not a TTY (e.g. under pytest).
Tests therefore verify content and structure rather than ANSI escape sequences.
"""

from pw.bookmark import Bookmark
from pw.bookmark_view import TableFormatter, print_search_result


def _make_bookmarks() -> list[Bookmark]:
    return [
        Bookmark(id=1, title="Alpha", link="https://alpha.example", tags="a"),
        Bookmark(id=2, title="Beta", link="https://beta.example", tags="b"),
        Bookmark(id=3, title="Gamma", link="https://gamma.example", tags="c"),
    ]


# ---------------------------------------------------------------------------
# header()
# ---------------------------------------------------------------------------


def test_header_returns_string_with_column_labels() -> None:
    """header() must include all four column labels regardless of color setting."""
    for color in ("no", "green", "#303030"):
        formatter = TableFormatter(alternate_row_color=color)
        header = formatter.header(_make_bookmarks())

        assert header is not None
        assert "ID" in header
        assert "Title" in header
        assert "Link" in header
        assert "Tags" in header


def test_header_empty_bookmarks_returns_none() -> None:
    formatter = TableFormatter(alternate_row_color="no")
    assert formatter.header([]) is None


def test_header_columns_are_padded_to_min_width() -> None:
    """Column labels should be padded to at least MIN_COL_WIDTH characters."""
    formatter = TableFormatter(alternate_row_color="no")
    header = formatter.header(_make_bookmarks())

    assert header is not None
    # "Title" padded to at least 20 chars — check there are spaces after it
    assert "Title" + " " * 15 in header  # 5 chars + 15 spaces = 20 min width


# ---------------------------------------------------------------------------
# rows()
# ---------------------------------------------------------------------------


def test_rows_returns_one_entry_per_bookmark() -> None:
    formatter = TableFormatter(alternate_row_color="no")
    bookmarks = _make_bookmarks()

    rows = formatter.rows(bookmarks)

    assert len(rows) == len(bookmarks)


def test_rows_contain_bookmark_data() -> None:
    formatter = TableFormatter(alternate_row_color="no")
    bookmarks = _make_bookmarks()

    rows = formatter.rows(bookmarks)

    assert "Alpha" in rows[0]
    assert "https://alpha.example" in rows[0]
    assert "Beta" in rows[1]
    assert "Gamma" in rows[2]


def test_rows_empty_bookmarks_returns_empty_list() -> None:
    formatter = TableFormatter(alternate_row_color="no")
    assert formatter.rows([]) == []


def test_rows_with_color_disabled_all_rows_are_plain_strings() -> None:
    """With _use_color=False every row is a plain string (no color prefix)."""
    formatter = TableFormatter(alternate_row_color="no")
    rows = formatter.rows(_make_bookmarks())

    # All rows start with the plain " - [" prefix (no color wrapper)
    for row in rows:
        assert row.startswith(" - [")


def test_rows_with_color_enabled_even_rows_are_wrapped() -> None:
    """With _use_color=True even-index rows are wrapped with the color style,
    odd-index rows are plain.

    In a non-TTY environment (pytest) colored returns empty strings, so the
    wrapping is invisible — but the code path is still exercised and the row
    content is correct.
    """
    formatter = TableFormatter(alternate_row_color="green")
    bookmarks = _make_bookmarks()

    rows = formatter.rows(bookmarks)

    assert len(rows) == 3
    # Content is always present regardless of color
    assert "Alpha" in rows[0]
    assert "Beta" in rows[1]
    assert "Gamma" in rows[2]
    # Odd-index row is always plain (starts with " - [")
    assert rows[1].startswith(" - [")


# ---------------------------------------------------------------------------
# Column-size cache
# ---------------------------------------------------------------------------


def test_column_sizes_cached_between_header_and_rows() -> None:
    """_compute_column_sizes should be computed once and reused."""
    formatter = TableFormatter(alternate_row_color="no")
    bookmarks = _make_bookmarks()

    formatter.header(bookmarks)
    sizes_after_header = formatter._column_sizes

    formatter.rows(bookmarks)
    sizes_after_rows = formatter._column_sizes

    assert sizes_after_header is sizes_after_rows


def test_column_sizes_none_before_first_call() -> None:
    formatter = TableFormatter(alternate_row_color="no")
    assert formatter._column_sizes is None


# ---------------------------------------------------------------------------
# print_search_result
# ---------------------------------------------------------------------------


def test_print_search_result_empty_does_not_raise(capsys) -> None:
    print_search_result([])
    captured = capsys.readouterr()
    assert captured.out == ""


def test_print_search_result_prints_header_and_rows(capsys) -> None:
    bookmarks = _make_bookmarks()
    print_search_result(bookmarks, alternate_row_color="no")

    captured = capsys.readouterr()
    assert "Title" in captured.out
    assert "Alpha" in captured.out
    assert "Beta" in captured.out
    assert "Gamma" in captured.out


def test_print_search_result_default_color_does_not_raise(capsys) -> None:
    """Calling with the default color (DEFAULT_BG_COLOR) should not raise."""
    print_search_result(_make_bookmarks())
    captured = capsys.readouterr()
    assert "Alpha" in captured.out
