"""SQLite writer for Sourcetrail-compatible index data."""

from __future__ import annotations

import json
import sqlite3
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from sourcetrail_remake.core.types import (
    AccessKind,
    DatabaseSummary,
    DefinitionKind,
    EdgeId,
    EdgeType,
    FileId,
    LocationId,
    NodeId,
    NodeType,
    SourceLocation,
)
from sourcetrail_remake.db.schema import STORAGE_VERSION, create_schema


class DatabaseWriter:
    """Persist indexer output into a Sourcetrail-compatible SQLite database."""

    def __init__(self, db_path: Path):
        self.db_path = Path(db_path).resolve()
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(self.db_path)
        self.connection.execute("PRAGMA foreign_keys = ON;")
        self.connection.execute("PRAGMA journal_mode = WAL;")
        self._files_by_path: dict[Path, FileId] = {}
        self._symbols_by_key: dict[tuple[str, int, int, int | None], NodeId] = {}
        self._edges_by_key: dict[tuple[int, int, int], EdgeId] = {}
        self._locations_by_key: dict[tuple[int, int, int, int, int, int], LocationId] = {}
        self._node_extensions: set[tuple[int, str]] = set()
        self._edge_extensions: set[tuple[int, str, str | None]] = set()
        self._next_element_id = 1
        self._next_location_id = 1

    def __enter__(self) -> DatabaseWriter:
        return self

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
        if exc is None:
            self.commit()
        else:
            self.connection.rollback()
        self.close()

    def initialize(self) -> None:
        self.initialize_schema()

    def initialize_schema(self) -> None:
        create_schema(self.connection, include_extensions=True)
        self._prime_counters()
        self.insert_meta("storage_version", str(STORAGE_VERSION))

    def insert_meta(self, key: str, value: str) -> None:
        row = self.connection.execute("SELECT id FROM meta WHERE key = ?;", (key,)).fetchone()
        if row is None:
            next_id = self.connection.execute("SELECT COALESCE(MAX(id), 0) + 1 FROM meta;").fetchone()
            assert next_id is not None
            self.connection.execute(
                "INSERT INTO meta(id, key, value) VALUES(?, ?, ?);",
                (int(next_id[0]), key, value),
            )
            return
        self.connection.execute("UPDATE meta SET value = ? WHERE key = ?;", (value, key))

    def record_file(self, path: Path, source: str | None = None) -> FileId:
        resolved_path = Path(path).resolve()
        existing = self._files_by_path.get(resolved_path)
        if existing is not None:
            return existing

        text = source if source is not None else resolved_path.read_text(encoding="utf-8")
        line_count = 0 if not text else text.count("\n") + 1
        modification_time = (
            datetime.fromtimestamp(resolved_path.stat().st_mtime, tz=UTC).isoformat()
            if resolved_path.exists()
            else datetime.now(tz=UTC).isoformat()
        )
        file_id = FileId(self._allocate_element_id())
        self._insert_element(int(file_id))
        self.connection.execute(
            "INSERT INTO node(id, type, serialized_name) VALUES(?, ?, ?);",
            (int(file_id), int(NodeType.NODE_FILE), str(resolved_path)),
        )
        self.connection.execute(
            (
                "INSERT INTO file("
                "id, path, language, modification_time, indexed, complete, line_count"
                ") VALUES(?, ?, ?, ?, ?, ?, ?);"
            ),
            (int(file_id), str(resolved_path), "python", modification_time, 1, 1, line_count),
        )
        self.connection.execute(
            "INSERT INTO filecontent(id, content) VALUES(?, ?);",
            (int(file_id), text),
        )
        self._files_by_path[resolved_path] = file_id
        return file_id

    def record_symbol(
        self,
        name: str,
        node_type: NodeType,
        file: FileId | None,
        location: SourceLocation | None,
        *,
        qualified_name: str | None = None,
        definition_kind: DefinitionKind = DefinitionKind.DEFINITION_EXPLICIT,
        access_kind: AccessKind | None = None,
    ) -> NodeId:
        serialized_name = qualified_name or name
        file_key = int(file) if file is not None else 0
        location_key = None if location is None else (
            (
                location.start_line,
                location.start_column,
                location.end_line,
                location.end_column,
                int(location.type),
            )
        )
        key = (serialized_name, int(node_type), file_key, location_key)
        existing = self._symbols_by_key.get(key)
        if existing is not None:
            if file is not None and location is not None:
                self.record_occurrence(existing, self.record_source_location(file, location))
            return existing

        node_id = NodeId(self._allocate_element_id())
        self._insert_element(int(node_id))
        self.connection.execute(
            "INSERT INTO node(id, type, serialized_name) VALUES(?, ?, ?);",
            (int(node_id), int(node_type), serialized_name),
        )
        self.connection.execute(
            "INSERT INTO symbol(id, definition_kind) VALUES(?, ?);",
            (int(node_id), int(definition_kind)),
        )
        if access_kind is not None:
            self.connection.execute(
                "INSERT OR IGNORE INTO component_access(node_id, type) VALUES(?, ?);",
                (int(node_id), int(access_kind)),
            )
        if file is not None and location is not None:
            self.record_occurrence(node_id, self.record_source_location(file, location))
        self._symbols_by_key[key] = node_id
        return node_id

    def record_edge(
        self,
        source: NodeId,
        target: NodeId,
        edge_type: EdgeType,
        *,
        file: FileId | None = None,
        location: SourceLocation | None = None,
    ) -> EdgeId:
        return self.record_reference(source, target, edge_type, file=file, location=location)

    def record_reference(
        self,
        source: NodeId,
        target: NodeId,
        kind: EdgeType,
        *,
        file: FileId | None = None,
        location: SourceLocation | None = None,
    ) -> EdgeId:
        key = (int(source), int(target), int(kind))
        edge_id = self._edges_by_key.get(key)
        if edge_id is None:
            edge_id = EdgeId(self._allocate_element_id())
            self._insert_element(int(edge_id))
            self.connection.execute(
                "INSERT INTO edge(id, type, source_node_id, target_node_id) VALUES(?, ?, ?, ?);",
                (int(edge_id), int(kind), int(source), int(target)),
            )
            self._edges_by_key[key] = edge_id
        if file is not None and location is not None:
            self.record_occurrence(edge_id, self.record_source_location(file, location))
        return edge_id

    def record_source_location(self, file: FileId, location: SourceLocation) -> LocationId:
        key = (
            int(file),
            location.start_line,
            location.start_column,
            location.end_line,
            location.end_column,
            int(location.type),
        )
        existing = self._locations_by_key.get(key)
        if existing is not None:
            return existing

        location_id = LocationId(self._allocate_location_id())
        self.connection.execute(
            (
                "INSERT INTO source_location("
                "id, file_node_id, start_line, start_column, end_line, end_column, type"
                ") VALUES(?, ?, ?, ?, ?, ?, ?);"
            ),
            (
                int(location_id),
                int(file),
                location.start_line,
                location.start_column,
                location.end_line,
                location.end_column,
                int(location.type),
            ),
        )
        self._locations_by_key[key] = location_id
        return location_id

    def record_occurrence(self, element_id: NodeId | EdgeId, source_location_id: LocationId) -> None:
        self.connection.execute(
            "INSERT OR IGNORE INTO occurrence(element_id, source_location_id) VALUES(?, ?);",
            (int(element_id), int(source_location_id)),
        )

    def record_unsolved(
        self,
        context_node: NodeId,
        name: str,
        *,
        file: FileId | None = None,
        location: SourceLocation | None = None,
        confidence: float | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> NodeId:
        node_id = self.record_symbol(
            name,
            NodeType.NODE_SYMBOL,
            file,
            location,
            qualified_name=f"unsolved.{int(context_node)}.{name}",
            definition_kind=DefinitionKind.DEFINITION_NONE,
        )
        extension_key = (int(node_id), "unsolved")
        if extension_key not in self._node_extensions:
            self.connection.execute(
                "INSERT INTO node_extension(node_id, kind, confidence, metadata) VALUES(?, ?, ?, ?);",
                (
                    int(node_id),
                    "unsolved",
                    confidence,
                    None if metadata is None else json.dumps(metadata, sort_keys=True),
                ),
            )
            self._node_extensions.add(extension_key)
        return node_id

    def record_edge_extension(
        self,
        edge_id: EdgeId,
        kind: str,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        encoded_metadata = None if metadata is None else json.dumps(metadata, sort_keys=True)
        key = (int(edge_id), kind, encoded_metadata)
        if key in self._edge_extensions:
            return
        self.connection.execute(
            "INSERT INTO edge_extension(edge_id, kind, metadata) VALUES(?, ?, ?);",
            (int(edge_id), kind, encoded_metadata),
        )
        self._edge_extensions.add(key)

    def summary(self) -> DatabaseSummary:
        def count(table: str) -> int:
            row = self.connection.execute(f"SELECT COUNT(*) FROM {table};").fetchone()
            assert row is not None
            return int(row[0])

        return DatabaseSummary(
            files=count("file"),
            symbols=count("symbol"),
            edges=count("edge"),
            locations=count("source_location"),
            occurrences=count("occurrence"),
            unsolved=int(
                self.connection.execute(
                    "SELECT COUNT(*) FROM node_extension WHERE kind = 'unsolved';"
                ).fetchone()[0]
            ),
        )

    def commit(self) -> None:
        self.connection.commit()

    def close(self) -> None:
        self.connection.close()

    def _insert_element(self, element_id: int) -> None:
        self.connection.execute("INSERT INTO element(id) VALUES(?);", (element_id,))

    def _allocate_element_id(self) -> int:
        element_id = self._next_element_id
        self._next_element_id += 1
        return element_id

    def _allocate_location_id(self) -> int:
        location_id = self._next_location_id
        self._next_location_id += 1
        return location_id

    def _prime_counters(self) -> None:
        element_row = self.connection.execute("SELECT COALESCE(MAX(id), 0) FROM element;").fetchone()
        location_row = self.connection.execute("SELECT COALESCE(MAX(id), 0) FROM source_location;").fetchone()
        assert element_row is not None
        assert location_row is not None
        self._next_element_id = int(element_row[0]) + 1
        self._next_location_id = int(location_row[0]) + 1
