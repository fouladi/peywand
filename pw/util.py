from argparse import ArgumentParser, RawTextHelpFormatter

DEFAULT_BG_COLOR = "#303030"


def arg_setup():
    """parsing of all input arguments"""

    pars = ArgumentParser(
        "peywand.py",
        usage="%(prog)s  {init, add, list, delete, update, import, export, version} [options]",
        formatter_class=RawTextHelpFormatter,
        description="""Init and manage a DB for your bookmarks

        Usage Examples:
        ~~~~~~~~~~~~~~~
        peywand.py init

        peywand.py add -t "Hacker News" -l "https://news.ycombinator.com/" -g "dev;news"
        peywand.py list -g "dev"
        peywand.py list
        peywand.py delete -i 4
        peywand.py delete -t "Hacker News" -l "https://news.ycom.com/"
        peywand.py update -i 5 -t "FarFar" -l "https://news.news.com/" -g "news"
        peywand.py export -f json -n bookmarks.json

        peywand.py version
            """,
    )
    subparser = pars.add_subparsers(dest="command")

    # init ------------------------------
    _ = subparser.add_parser("init", help="Init bookmark db")

    # add ------------------------------
    read_parser = subparser.add_parser("add", help="Add a bookmark")
    read_parser.add_argument("-t", "--title", help="Title of bookmark", type=str, required=True)
    read_parser.add_argument("-l", "--link", help="URL of bookmark", type=str, required=True)
    read_parser.add_argument("-g", "--tags", help="one or more tags seperated with ;", type=str, required=True)

    # list ------------------------------
    list_parser = subparser.add_parser("list", help="Search and list for bookmarks")
    list_parser.add_argument("-t", "--title", help="Filter search results by specified title", default=None, type=str)
    list_parser.add_argument("-l", "--link", help="Filter search results by specified link", default=None, type=str)
    list_parser.add_argument(
        "-g",
        "--tags",
        help='Tags associates to the artifact to search in the form "tag1;tag2;...;tagN"',
        default=None,
        type=str,
    )
    list_parser.add_argument(
        "-c",
        "--row_bg_color",
        dest="row_bg_color",
        choices=["no", "light_gray", "dark_gray", "dark_green", "light_green"],
        default=DEFAULT_BG_COLOR,
        help="Row background color (choices: no, light_gray, dark_gray, dark_green, light_green)",
    )

    # delete ------------------------------
    delete_parser = subparser.add_parser("delete", help="Delete bookmark")
    delete_parser.add_argument("-i", "--id", help="ID of the bookmark", type=str, nargs="*")
    delete_parser.add_argument("-t", "--title", help="Title of the bookmark to remove", default=None, type=str)
    delete_parser.add_argument("-l", "--link", help="Link associated to the artifact to remove", default=None, type=str)

    # update ------------------------------
    update_parser = subparser.add_parser("update", help="Update bookmark properties")
    update_parser.add_argument("-i", "--id", help="ID of the artifact to update", type=str, required=True)
    update_parser.add_argument("-t", "--title", help="Title to update", default=None, type=str, required=True)
    update_parser.add_argument("-l", "--link", help="Link to update", default=None, type=str, required=True)
    update_parser.add_argument(
        "-g", "--tags", help='Tags to update in the form "tag1;tag2;...;tagN"', default=None, type=str, required=True
    )

    # import ------------------------------
    import_parser = subparser.add_parser("import", help="Import all bookmarks from a given HTML file")
    import_parser.add_argument("-n", "--file_name", help="Name of imported file", type=str, required=True)
    import_parser.add_argument(
        "-f",
        "--file_format",
        help="Format of imported file",
        dest="file_format",
        choices=["html", "json"],
        type=str,
        required=True,
    )

    # export ------------------------------
    export_parser = subparser.add_parser("export", help="Export all bookmarks to a given file")
    export_parser.add_argument("-n", "--file_name", help="Name of exported file", type=str, required=True)
    export_parser.add_argument(
        "-f",
        "--file_format",
        help="Format of exported file",
        dest="file_format",
        choices=["html", "json"],
        type=str,
        required=True,
    )

    # version ------------------------------
    _ = subparser.add_parser("version", help="Print out the current version")

    return pars.parse_args()


argpars = arg_setup()
