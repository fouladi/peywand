from argparse import ArgumentParser
from pathlib import Path

DEFAULT_BG_COLOR = "#303030"


def build_launcher_parser() -> ArgumentParser:
    """Build the CLI parser for launching the Textual application."""

    parser = ArgumentParser(
        "peywand.py",
        description="Peywand Textual bookmark manager.",
    )
    parser.add_argument(
        "--db-path",
        default=str(Path.home() / ".pw.db"),
        help="Path to the SQLite database file.",
    )
    parser.add_argument(
        "--version",
        action="store_true",
        help="Print the current Peywand version and exit.",
    )
    return parser
