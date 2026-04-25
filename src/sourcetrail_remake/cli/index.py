"""Headless indexer CLI scaffold."""

from __future__ import annotations

import argparse
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Phase 0 indexer scaffold.")
    parser.add_argument("project_path", type=Path, help="Project directory to index.")
    parser.add_argument("--db", type=Path, default=None, help="Destination .srctrldb path.")
    return parser


def main(argv: list[str] | None = None) -> int:
    """Validate arguments for the future indexer entrypoint."""
    parser = build_parser()
    args = parser.parse_args(argv)

    if not args.project_path.exists():
        parser.error(f"Project path does not exist: {args.project_path}")

    logger.info("Indexer scaffold invoked for %s", args.project_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
