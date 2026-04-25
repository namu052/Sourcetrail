"""Headless indexer CLI scaffold."""

from __future__ import annotations

import argparse
import logging
from pathlib import Path
import sys

from PyQt6.QtCore import QCoreApplication

from sourcetrail_remake.indexer.service import IndexerService, IndexingWorker

logger = logging.getLogger(__name__)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Index a Python project into a Sourcetrail-compatible DB.")
    parser.add_argument("project_path", type=Path, help="Project directory to index.")
    parser.add_argument("--db", type=Path, default=None, help="Destination .srctrldb path.")
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument("--shallow", action="store_true", help="Use fast name-based indexing.")
    mode_group.add_argument("--deep", action="store_true", help="Use Jedi-backed deep resolution.")
    return parser


def main(argv: list[str] | None = None) -> int:
    """Index a Python project in a background QThread and wait for completion."""
    parser = build_parser()
    args = parser.parse_args(argv)

    if not args.project_path.exists():
        parser.error(f"Project path does not exist: {args.project_path}")

    logging.basicConfig(level=logging.INFO, format="%(message)s")
    project_path = args.project_path.resolve()
    db_path = args.db.resolve() if args.db is not None else Path.cwd() / f"{project_path.name}.srctrldb"
    mode = "deep" if args.deep else "shallow"

    app = QCoreApplication.instance()
    if app is None:
        app = QCoreApplication([sys.argv[0]])
    else:
        assert isinstance(app, QCoreApplication)

    service = IndexerService(project_path, mode)
    worker = IndexingWorker(service, db_path)
    exit_code = 0
    result_holder: dict[str, object] = {}

    def on_progress(current: int, total: int) -> None:
        logger.info("Indexing %s/%s", current, total)

    def on_completed(result: object) -> None:
        result_holder["result"] = result
        app.quit()

    def on_failed(message: str) -> None:
        nonlocal exit_code
        exit_code = 1
        logger.error("Indexing failed: %s", message)
        app.quit()

    worker.progress_changed.connect(on_progress)
    worker.completed.connect(on_completed)
    worker.failed.connect(on_failed)
    worker.start()
    app.exec()
    worker.wait()

    if exit_code == 0:
        logger.info("Indexed %s -> %s", project_path, db_path.resolve())
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
