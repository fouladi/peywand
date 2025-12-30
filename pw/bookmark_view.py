from collections.abc import Iterable

import colored

from pw.bookmark import Bookmark

ALT_BGROUND = colored.bg("#303030")
BOLD = colored.attr("bold")
UNDERLINE = colored.attr("underline")
RESET = colored.attr("reset")  # reset the style and colors back to default

MIN_COL_WIDTH = 20


def _column_width(
    values: Iterable[str],
    *,
    minimum: int = MIN_COL_WIDTH,
) -> int:
    """Calculate the column width for a table column.

    The width is determined by the longest string in *values* and is
    guaranteed to be at least *minimum* characters wide.

    Args:
        values:
            Iterable of strings whose lengths are evaluated.
        minimum:
            Minimum column width to enforce.
    Returns:
        The computed column width as an integer.
    """
    width = max((len(value) for value in values), default=0)
    return max(width, minimum)


def _compute_column_sizes(bookmarks: list[Bookmark]) -> tuple[int, int, int, int]:
    """Compute column widths for bookmark table output.

    The calculated widths correspond to:
         - ID column
         - Title column
         - Link column
         - Tags column

     Args:
         bookmarks:
             List of bookmarks to be displayed.
     Returns:
         A tuple of four integers:
         (id_width, title_width, link_width, tags_width).
    """
    len_id = max(len(str(len(bookmarks) - 1)), 2)
    len_title = _column_width(b.title or "" for b in bookmarks)
    len_link = _column_width(b.link or "" for b in bookmarks)
    len_tags = _column_width(b.tags or "" for b in bookmarks)

    return len_id, len_title, len_link, len_tags


def generate_search_header(
    search_result: list[Bookmark],
    *,
    color: bool = True,
) -> str | None:
    """Generate the table header for bookmark search results.

    Args:
        search_result:
            List of bookmarks that will be printed.
        color:
            If True, apply terminal styling (bold + underline).

    Returns:
        The formatted header string, or None if the result list is empty.
    """
    if not search_result:
        return None

    len_id, len_title, len_link, len_tags = _compute_column_sizes(search_result)

    header = (
        f"   [ {'ID'.rjust(len_id)} ]  {'Title'.ljust(len_title)} {'Link'.ljust(len_link)} {'Tags'.ljust(len_tags)}"
    )
    return f"{UNDERLINE}{BOLD}{header}{RESET}" if color else header


def print_search_result(
    search_result: list[Bookmark],
    *,
    color: bool = True,
) -> None:
    """Print bookmark search results in a formatted table.

    Each bookmark is printed on its own line. When color output is enabled,
    alternating rows are highlighted for better readability.

    Args:
        search_result:
            List of bookmarks to display.
        color:
            If True, apply terminal background styling.
    Returns:
        None
    """
    if not search_result:
        return

    header = generate_search_header(search_result, color=color)
    if header:
        print(header)
        print()

    len_id, len_title, len_link, len_tags = _compute_column_sizes(search_result)

    for index, bookmark in enumerate(search_result):
        line = (
            f" - [ {str(bookmark.id).rjust(len_id)} ]  "
            f"{bookmark.title.ljust(len_title)} "
            f"{bookmark.link.ljust(len_link)} "
            f"{(bookmark.tags or '').ljust(len_tags)}"
        )

        if color and index % 2 == 0:
            print(f"{ALT_BGROUND}{line}{RESET}")
        else:
            print(line)
