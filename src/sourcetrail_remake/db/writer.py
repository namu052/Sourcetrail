"""Minimal SQLite writer for Phase 0 PoCs."""

from __future__ import annotations

import sqlite3
from pathlib import Path

from sourcetrail_remake.db.schema import STORAGE_VERSION, create_schema


class DatabaseWriter:
    """Small helper around SQLite writes for PoC generation."""

    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.connection = sqlite3.connect(db_path)
        self.connection.execute("PRAGMA foreign_keys = ON;")

    def initialize(self) -> None:
        create_schema(self.connection, include_extensions=True)
        self.insert_meta("storage_version", str(STORAGE_VERSION))

    def insert_meta(self, key: str, value: str) -> None:
        self.connection.execute(
            "INSERT INTO meta(id, key, value) VALUES((SELECT id FROM meta WHERE key = ?), ?, ?);",
            (key, key, value),
        )

    def insert_element(self, element_id: int) -> None:
        self.connection.execute("INSERT INTO element(id) VALUES(?);", (element_id,))

    def insert_node(self, element_id: int, node_type: int, serialized_name: str) -> None:
        self.insert_element(element_id)
        self.connection.execute(
            "INSERT INTO node(id, type, serialized_name) VALUES(?, ?, ?);",
            (element_id, node_type, serialized_name),
        )

    def insert_symbol(self, node_id: int, definition_kind: int) -> None:
        self.connection.execute(
            "INSERT INTO symbol(id, definition_kind) VALUES(?, ?);",
            (node_id, definition_kind),
        )

    def insert_edge(
        self,
        edge_id: int,
        edge_type: int,
        source_node_id: int,
        target_node_id: int,
    ) -> None:
        self.insert_element(edge_id)
        self.connection.execute(
            "INSERT INTO edge(id, type, source_node_id, target_node_id) VALUES(?, ?, ?, ?);",
            (edge_id, edge_type, source_node_id, target_node_id),
        )

    def insert_file(
        self,
        file_id: int,
        path: str,
        language: str,
        modification_time: str,
        indexed: int,
        complete: int,
        line_count: int,
        content: str,
    ) -> None:
        self.insert_node(file_id, 1 << 18, path)
        self.connection.execute(
            (
                "INSERT INTO file("
                "id, path, language, modification_time, indexed, complete, line_count"
                ") "
                "VALUES(?, ?, ?, ?, ?, ?, ?);"
            ),
            (file_id, path, language, modification_time, indexed, complete, line_count),
        )
        self.connection.execute(
            "INSERT INTO filecontent(id, content) VALUES(?, ?);",
            (file_id, content),
        )

    def insert_source_location(
        self,
        location_id: int,
        file_node_id: int,
        start_line: int,
        start_column: int,
        end_line: int,
        end_column: int,
        location_type: int,
    ) -> None:
        self.connection.execute(
            (
                "INSERT INTO source_location(id, file_node_id, start_line, start_column, end_line, "
                "end_column, type) VALUES(?, ?, ?, ?, ?, ?, ?);"
            ),
            (
                location_id,
                file_node_id,
                start_line,
                start_column,
                end_line,
                end_column,
                location_type,
            ),
        )

    def insert_occurrence(self, element_id: int, source_location_id: int) -> None:
        self.connection.execute(
            "INSERT INTO occurrence(element_id, source_location_id) VALUES(?, ?);",
            (element_id, source_location_id),
        )

    def insert_node_extension(
        self,
        node_id: int,
        kind: str,
        confidence: float | None,
        metadata: str,
    ) -> None:
        self.connection.execute(
            "INSERT INTO node_extension(node_id, kind, confidence, metadata) VALUES(?, ?, ?, ?);",
            (node_id, kind, confidence, metadata),
        )

    def commit(self) -> None:
        self.connection.commit()

    def close(self) -> None:
        self.connection.close()
