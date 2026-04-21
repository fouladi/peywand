#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

from pw import __version__ as pw_version
from pw.util import build_launcher_parser


def main() -> None:
    args = build_launcher_parser().parse_args()

    if args.version:
        print(f"Current version: {pw_version}")
        return

    try:
        from pw.tui import PeywandApp
    except ModuleNotFoundError as error:
        if error.name == "textual":
            raise SystemExit(
                "Textual is required to run Peywand. Install dependencies with "
                "`python -m pip install .` or `python -m pip install textual`."
            ) from error
        raise

    PeywandApp(Path(args.db_path).expanduser()).run()


if __name__ == "__main__":
    main()
