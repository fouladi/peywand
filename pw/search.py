"""Module for printing the result on terminal"""

import colored

from pw.bookmark import Bookmark

ALT_BGROUND = colored.bg("#303030")
BOLD = colored.attr("bold")
UNDERLINE = colored.attr("underline")
RESET = colored.attr("reset")  # reset the style and colors back to default


def generate_search_header(search_result: list[Bookmark], color: bool = True) -> str | None:
    """Generates query search results header.

    Arguments:
        search_result   - the list of Bookmarks for generating
                        an adapted header
        color           - a boolean, True if color is enabled

    Returns:
        A string representing the header for the list of bookmarks
    """

    if not search_result:
        return

    min_length = 20
    len_id = max(len(str(len(search_result) - 1)), 2)
    len_title = max(max([len(art.title) if art.title else 0 for art in search_result]), min_length)
    len_categ = max(max([len(art.link) if art.link else 0 for art in search_result]), min_length)
    len_tags = max(max([len(art.tags) if art.tags else 0 for art in search_result]), min_length)

    header = "   [ {id} ]  {title} {link} {tags}".format(
        id="ID".rjust(len_id),
        title="Title".ljust(len_title),
        link="Link".ljust(len_categ),
        tags="Tags".ljust(len_tags),
    )
    if color:
        return UNDERLINE + BOLD + header + RESET
    return header


def print_search_result(search_result: list[Bookmark], color: bool = True) -> None:
    """Print query search results

    Arguments:
        search_result   - the list of Bookmarks to print
                        in the form of search result
        color           - a boolean, True if color is enabled
    """
    if not search_result:
        return
    print(generate_search_header(search_result, color=color))
    print()

    min_length = 20
    len_id = max(len(str(len(search_result) - 1)), 2)
    len_title = max(max([len(art.title) if art.title else 0 for art in search_result]), min_length)
    len_categ = max(max([len(art.link) if art.link else 0 for art in search_result]), min_length)
    len_tags = max(max([len(art.tags) if art.tags else 0 for art in search_result]), min_length)

    # Print results
    for view_id, bookmark in enumerate(search_result):
        tags = bookmark.tags if bookmark.tags else ""

        result_line = f" - [ {str(bookmark.id).rjust(len_id)} ]  {bookmark.title.ljust(len_title)} {bookmark.link.ljust(len_categ)} {tags.ljust(len_tags)}"
        if color and (view_id % 2 == 0):
            print(ALT_BGROUND + result_line + RESET)
        else:
            print(result_line)
