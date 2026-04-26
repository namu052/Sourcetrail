"""Generate and validate a Sourcetrail-compatible DB for a fixture project."""

from __future__ import annotations

import json
import sqlite3
import sys
from datetime import UTC, datetime
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

from sourcetrail_remake.db.writer import DatabaseWriter
from sourcetrail_remake.indexer.service import IndexerService

REQUIRED_TABLES = {
    "component_access",
    "edge",
    "edge_extension",
    "element",
    "error",
    "file",
    "filecontent",
    "local_symbol",
    "meta",
    "node",
    "node_extension",
    "node_file",
    "occurrence",
    "source_location",
    "symbol",
}

REQUIRED_COLUMNS = {
    "node": {"id", "type", "serialized_name"},
    "edge": {"id", "type", "source_node_id", "target_node_id"},
    "symbol": {"id", "definition_kind"},
    "file": {"id", "path", "language", "modification_time", "indexed", "complete", "line_count"},
    "source_location": {
        "id",
        "file_node_id",
        "start_line",
        "start_column",
        "end_line",
        "end_column",
        "type",
    },
    "occurrence": {"element_id", "source_location_id"},
    "meta": {"id", "key", "value"},
    "node_extension": {"node_id", "kind", "confidence", "metadata"},
    "edge_extension": {"edge_id", "kind", "metadata"},
}


def main(argv: list[str] | None = None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    fixture = Path(args[0] if args else "tests/fixtures/sample-minimal").resolve()
    if not fixture.is_dir():
        raise SystemExit(f"compat-check: fixture not found: {fixture}")

    with TemporaryDirectory(prefix="srm-compat-", ignore_cleanup_errors=True) as temp_dir:
        db_path = Path(temp_dir) / f"{fixture.name}.srctrldb"
        with DatabaseWriter(db_path) as writer:
            result = IndexerService(fixture, "shallow").index(writer, lambda _current, _total: None)

        report = _validate_database(db_path)
        report.update(
            {
                "fixture": str(fixture),
                "db_path": str(db_path),
                "index_result": {
                    "files_indexed": result.files_indexed,
                    "symbols_recorded": result.symbols_recorded,
                    "edges_recorded": result.edges_recorded,
                    "unsolved_symbols": result.unsolved_symbols,
                    "duration_seconds": result.duration_seconds,
                },
                "original_sourcetrail_gui": "not_available_in_automated_check",
            }
        )

    report_path = _write_report(report)
    if report["status"] != "pass":
        print(f"compat-check: FAILED -> {report_path}")
        print(json.dumps(report, indent=2, sort_keys=True))
        return 1
    print(f"compat-check: OK -> {report_path}")
    return 0


def _validate_database(db_path: Path) -> dict[str, Any]:
    with sqlite3.connect(db_path) as connection:
        tables = {
            row[0]
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table';"
            ).fetchall()
        }
        missing_tables = sorted(REQUIRED_TABLES - tables)
        missing_columns: dict[str, list[str]] = {}
        for table, required_columns in REQUIRED_COLUMNS.items():
            if table not in tables:
                continue
            columns = {row[1] for row in connection.execute(f"PRAGMA table_info({table});")}
            missing = sorted(required_columns - columns)
            if missing:
                missing_columns[table] = missing

        foreign_key_violations = [
            tuple(row) for row in connection.execute("PRAGMA foreign_key_check;").fetchall()
        ]
        counts = {
            table: int(connection.execute(f"SELECT COUNT(*) FROM {table};").fetchone()[0])
            for table in ("node", "edge", "symbol", "file", "source_location", "occurrence")
            if table in tables
        }

    status = "pass"
    if missing_tables or missing_columns or foreign_key_violations:
        status = "fail"
    return {
        "status": status,
        "missing_tables": missing_tables,
        "missing_columns": missing_columns,
        "foreign_key_violations": foreign_key_violations,
        "counts": counts,
    }


def _write_report(report: dict[str, Any]) -> Path:
    output_dir = Path("docs/generated/compat")
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(tz=UTC).strftime("%Y%m%d-%H%M%S")
    report_path = output_dir / f"{timestamp}.json"
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    return report_path


if __name__ == "__main__":
    raise SystemExit(main())
