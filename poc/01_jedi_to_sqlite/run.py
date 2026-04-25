"""Generate a minimal SourcetrailDB-shaped SQLite database from a sample fixture."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

from sourcetrail_remake.db.compat import missing_required_tables
from sourcetrail_remake.db.schema import (
    DEFINITION_KIND_VALUES,
    EDGE_TYPE_VALUES,
    NODE_KIND_VALUES,
    SOURCE_LOCATION_VALUES,
)
from sourcetrail_remake.db.writer import DatabaseWriter
from sourcetrail_remake.indexer.jedi_resolver import JediResolver

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "tests" / "fixtures" / "sample-minimal" / "session_manager.py"
ARTIFACT_DIR = Path(__file__).resolve().parent / "artifacts"
DB_PATH = ARTIFACT_DIR / "sample-minimal.srctrldb"
REPORT_PATH = ARTIFACT_DIR / "report.json"
FIXTURE_RELATIVE_PATH = FIXTURE.relative_to(ROOT)
DB_RELATIVE_PATH = DB_PATH.relative_to(ROOT)


def node_kind_for(symbol_type: str) -> int:
    return {
        "class": NODE_KIND_VALUES["NODE_CLASS"],
        "function": NODE_KIND_VALUES["NODE_FUNCTION"],
        "instance": NODE_KIND_VALUES["NODE_GLOBAL_VARIABLE"],
        "param": NODE_KIND_VALUES["NODE_TYPE_PARAMETER"],
    }.get(symbol_type, NODE_KIND_VALUES["NODE_SYMBOL"])


def main() -> int:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    if DB_PATH.exists():
        DB_PATH.unlink()

    source = FIXTURE.read_text(encoding="utf-8")
    resolver = JediResolver(project_root=FIXTURE.parent)
    definitions = resolver.collect_definitions(source, FIXTURE)

    writer = DatabaseWriter(DB_PATH)
    writer.initialize()
    writer.insert_meta("project_name", "sample-minimal")
    writer.insert_file(
        file_id=1,
        path=FIXTURE_RELATIVE_PATH.as_posix(),
        language="python",
        modification_time=datetime.fromtimestamp(FIXTURE.stat().st_mtime, UTC).isoformat(),
        indexed=1,
        complete=1,
        line_count=len(source.splitlines()),
        content=source,
    )

    next_node_id = 100
    next_location_id = 1000
    next_edge_id = 5000

    created_nodes: list[dict[str, object]] = []
    for definition in definitions:
        node_id = next_node_id
        next_node_id += 1
        writer.insert_node(node_id, node_kind_for(definition.symbol_type), definition.name)
        writer.insert_symbol(node_id, DEFINITION_KIND_VALUES["DEFINITION_EXPLICIT"])
        writer.insert_source_location(
            location_id=next_location_id,
            file_node_id=1,
            start_line=definition.line,
            start_column=definition.column,
            end_line=definition.line,
            end_column=definition.column + len(definition.name),
            location_type=SOURCE_LOCATION_VALUES["LOCATION_TOKEN"],
        )
        writer.insert_occurrence(node_id, next_location_id)
        writer.insert_edge(next_edge_id, EDGE_TYPE_VALUES["EDGE_MEMBER"], 1, node_id)
        created_nodes.append(
            {"id": node_id, "name": definition.name, "type": definition.symbol_type}
        )
        next_location_id += 1
        next_edge_id += 1

    unsolved_id = next_node_id
    writer.insert_node(unsolved_id, NODE_KIND_VALUES["NODE_SYMBOL"], "missing_cleanup_handler")
    writer.insert_symbol(unsolved_id, DEFINITION_KIND_VALUES["DEFINITION_NONE"])
    writer.insert_node_extension(
        unsolved_id,
        "unsolved",
        0.15,
        json.dumps({"reason": "fixture reference"}),
    )
    writer.insert_edge(next_edge_id, EDGE_TYPE_VALUES["EDGE_USAGE"], 1, unsolved_id)

    writer.commit()
    writer.close()

    missing_tables = missing_required_tables(DB_PATH)
    report = {
        "fixture": FIXTURE_RELATIVE_PATH.as_posix(),
        "database": DB_RELATIVE_PATH.as_posix(),
        "definition_count": len(created_nodes),
        "unsolved_symbol_count": 1,
        "missing_tables": missing_tables,
        "created_nodes": created_nodes,
    }
    REPORT_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
