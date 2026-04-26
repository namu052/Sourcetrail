"""Native Phase 1 benchmark fallback used when pytest-benchmark is unavailable."""

from __future__ import annotations

import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from tempfile import TemporaryDirectory
from time import perf_counter

from PyQt6.QtWidgets import QApplication

from sourcetrail_remake.core.event_bus import EventBus
from sourcetrail_remake.core.types import NodeId
from sourcetrail_remake.db.reader import DatabaseReader
from sourcetrail_remake.db.writer import DatabaseWriter
from sourcetrail_remake.indexer.service import IndexerService
from sourcetrail_remake.ui.graph.scene import GraphScene


def main(argv: list[str] | None = None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    output_path = Path(args[0] if args else "docs/generated/bench/phase1.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    app = QApplication.instance()
    if app is None:
        app = QApplication([sys.argv[0]])

    with TemporaryDirectory(prefix="srm-bench-", ignore_cleanup_errors=True) as temp_dir:
        temp_root = Path(temp_dir)
        project_root = temp_root / "synthetic-10k-loc"
        _write_synthetic_project(project_root)
        db_path = temp_root / "synthetic.srctrldb"

        index_started = perf_counter()
        with DatabaseWriter(db_path) as writer:
            index_result = IndexerService(project_root, "shallow").index(
                writer, lambda _current, _total: None
            )
        index_seconds = perf_counter() - index_started

        reader = DatabaseReader(db_path)
        symbols = reader.list_symbols()
        root_id = symbols[0].id if symbols else NodeId(1)
        scene = GraphScene(reader=reader, event_bus=EventBus())
        render_started = perf_counter()
        scene.load_symbol(root_id, depth=2)
        render_seconds = perf_counter() - render_started

    status = "pass"
    report = {
        "created_at": datetime.now(tz=UTC).isoformat(),
        "status": status,
        "benchmarks": {
            "synthetic_10k_loc_shallow_index_seconds": index_seconds,
            "graph_first_render_seconds": render_seconds,
        },
        "thresholds": {
            "synthetic_10k_loc_shallow_index_seconds": 60.0,
            "graph_first_render_seconds": 0.5,
        },
        "index_result": {
            "files_indexed": index_result.files_indexed,
            "symbols_recorded": index_result.symbols_recorded,
            "edges_recorded": index_result.edges_recorded,
            "unsolved_symbols": index_result.unsolved_symbols,
        },
        "notes": [
            "Native fallback benchmark; pytest-benchmark is not installed.",
            "G2 100k LoC 60fps remains a separate manual/performance-lab gate.",
        ],
    }
    if index_seconds >= 60.0 or render_seconds >= 0.5:
        status = "fail"
        report["status"] = status

    output_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    print(f"bench: {status.upper()} -> {output_path}")
    print(f"bench: shallow_index={index_seconds:.3f}s graph_first_render={render_seconds:.3f}s")
    return 0 if status == "pass" else 1


def _write_synthetic_project(project_root: Path) -> None:
    project_root.mkdir(parents=True, exist_ok=True)
    for module_index in range(50):
        lines = [
            f"class Service{module_index}:",
            "    def __init__(self) -> None:",
            "        self.value = 0",
        ]
        for method_index in range(20):
            lines.extend(
                [
                    f"    def method_{method_index}(self, value: int) -> int:",
                    "        self.value += value",
                    "        return self.value",
                    "",
                ]
            )
        while len(lines) < 200:
            lines.append(f"CONSTANT_{len(lines)} = {len(lines)}")
        (project_root / f"module_{module_index}.py").write_text(
            "\n".join(lines) + "\n", encoding="utf-8"
        )


if __name__ == "__main__":
    raise SystemExit(main())
