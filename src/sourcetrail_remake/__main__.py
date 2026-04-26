"""Package entrypoint for the Phase 0 scaffold."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QApplication

from sourcetrail_remake.core.config import configure_qt_application
from sourcetrail_remake.core.event_bus import EventBus
from sourcetrail_remake.db.reader import DatabaseReader
from sourcetrail_remake.ui.main_window import create_main_window


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Launch the Sourcetrail_Remake graph UI.")
    parser.add_argument(
        "db_path",
        nargs="?",
        help="Optional SourcetrailDB path to open on launch.",
    )
    parser.add_argument(
        "--symbol",
        default=None,
        help="Optional fully qualified symbol name to focus after loading the DB.",
    )
    parser.add_argument(
        "--auto-quit-ms",
        type=int,
        default=None,
        help="Quit automatically after N milliseconds. Useful for headless smoke tests.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Launch the Phase 1 graph shell with optional DB bootstrap."""
    parser = build_parser()
    args = parser.parse_args(argv)

    qt_argv = [sys.argv[0]]
    app = QApplication.instance()
    if app is None:
        app = QApplication(qt_argv)
    else:
        assert isinstance(app, QApplication)
    configure_qt_application(app)

    event_bus = EventBus()
    reader: DatabaseReader | None = None
    initial_symbol_id = None
    if args.db_path is not None:
        reader = DatabaseReader(Path(args.db_path).resolve())
        if args.symbol is not None:
            initial_symbol_id = reader.find_symbol_id(args.symbol)
        else:
            symbols = reader.list_symbols(limit=1)
            initial_symbol_id = symbols[0].id if symbols else None

    window = create_main_window(
        event_bus,
        reader=reader,
        initial_symbol_id=initial_symbol_id,
    )
    window.show()

    auto_quit_ms = args.auto_quit_ms
    if auto_quit_ms is None:
        env_value = os.getenv("SRM_AUTO_QUIT_MS")
        auto_quit_ms = int(env_value) if env_value else None
    if auto_quit_ms is not None:
        QTimer.singleShot(auto_quit_ms, app.quit)

    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
