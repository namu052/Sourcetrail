"""Package entrypoint for the Phase 0 scaffold."""

from __future__ import annotations

import argparse
import os
import sys

from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QApplication

from sourcetrail_remake.core.config import configure_qt_application
from sourcetrail_remake.core.event_bus import EventBus
from sourcetrail_remake.ui.main_window import create_main_window


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Launch the Phase 0 Sourcetrail_Remake shell.")
    parser.add_argument(
        "--auto-quit-ms",
        type=int,
        default=None,
        help="Quit automatically after N milliseconds. Useful for headless smoke tests.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Launch a minimal QMainWindow shell for Phase 0 validation."""
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
    window = create_main_window(event_bus)
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
