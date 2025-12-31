from collections.abc import Iterable

import colored

from pw.bookmark import Bookmark
from pw.util import DEFAULT_BG_COLOR

ALT_BGROUND = colored.back(DEFAULT_BG_COLOR)
BOLD = colored.style("bold")
UNDERLINE = colored.style("underline")
RESET = colored.style("reset")

MIN_COL_WIDTH = 20


class TableFormatter:
    """Formats tabular data for terminal output.

    The formatter computes column widths once and can generate
    headers and rows consistently.
    """

    def __init__(self, *, min_column_width: int = MIN_COL_WIDTH, alternate_row_color: str) -> None:
        self._min_column_width = min_column_width
        self._use_color = False if alternate_row_color == "no" else True
        self._alternate_row_style = ALT_BGROUND if alternate_row_color == "no" else colored.back(alternate_row_color)

    def _column_width(self, values: Iterable[str]) -> int:
        """Return the column width based on content and minimum width."""
        width = max((len(value) for value in values), default=0)
        return max(width, self._min_column_width)

    def _compute_column_sizes(
        self,
        bookmarks: list[Bookmark],
    ) -> tuple[int, int, int, int]:
        """Compute column widths for all bookmark fields."""
        len_id = max(len(str(len(bookmarks) - 1)), 2)
        len_title = self._column_width(b.title or "" for b in bookmarks)
        len_link = self._column_width(b.link or "" for b in bookmarks)
        len_tags = self._column_width(b.tags or "" for b in bookmarks)

        return len_id, len_title, len_link, len_tags

    def header(self, bookmarks: list[Bookmark]) -> str | None:
        """Return the formatted table header."""
        if not bookmarks:
            return None

        len_id, len_title, len_link, len_tags = self._compute_column_sizes(bookmarks)

        header = (
            f"   [ {'ID'.rjust(len_id)} ]  {'Title'.ljust(len_title)} {'Link'.ljust(len_link)} {'Tags'.ljust(len_tags)}"
        )
        return f"{UNDERLINE}{BOLD}{header}{RESET}" if self._alternate_row_style else header

    def rows(self, bookmarks: list[Bookmark]) -> list[str]:
        """Return formatted table rows for the given bookmarks."""
        if not bookmarks:
            return []

        len_id, len_title, len_link, len_tags = self._compute_column_sizes(bookmarks)
        lines: list[str] = []

        for index, bookmark in enumerate(bookmarks):
            line = (
                f" - [ {str(bookmark.id).rjust(len_id)} ]  "
                f"{bookmark.title.ljust(len_title)} "
                f"{bookmark.link.ljust(len_link)} "
                f"{(bookmark.tags or '').ljust(len_tags)}"
            )

            if self._use_color and index % 2 == 0:
                lines.append(f"{self._alternate_row_style}{line}{RESET}")
            else:
                lines.append(line)

        return lines


def print_search_result(search_result: list[Bookmark], alternate_row_color: str = DEFAULT_BG_COLOR) -> None:
    """Print bookmark search results in a formatted table.

    Each bookmark is printed on its own line. When color output is enabled,
    alternating rows are highlighted for better readability.
    """
    if not search_result:
        return

    formatter = TableFormatter(alternate_row_color=alternate_row_color)

    header = formatter.header(search_result)
    if header:
        print(header)
        print()

    for line in formatter.rows(search_result):
        print(line)
