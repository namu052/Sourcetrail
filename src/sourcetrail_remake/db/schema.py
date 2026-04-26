"""SourcetrailDB v25 schema constants and helpers."""

from __future__ import annotations

import sqlite3
from collections.abc import Iterable

from sourcetrail_remake.core.types import (
    AccessKind,
    DefinitionKind,
    EdgeType,
    NodeType,
    SourceLocationType,
)

STORAGE_VERSION = 25

REQUIRED_TABLES = (
    "meta",
    "element",
    "element_component",
    "edge",
    "node",
    "symbol",
    "file",
    "filecontent",
    "node_file",
    "local_symbol",
    "source_location",
    "occurrence",
    "component_access",
    "error",
)

REQUIRED_EXTENSION_TABLES = (
    "edge_extension",
    "node_extension",
)

SCHEMA_SQL = (
    "CREATE TABLE IF NOT EXISTS meta(id INTEGER, key TEXT, value TEXT, PRIMARY KEY(id));",
    "CREATE TABLE IF NOT EXISTS element(id INTEGER, PRIMARY KEY(id));",
    (
        "CREATE TABLE IF NOT EXISTS element_component("
        "id INTEGER, element_id INTEGER, type INTEGER, data TEXT, PRIMARY KEY(id), "
        "FOREIGN KEY(element_id) REFERENCES element(id) ON DELETE CASCADE);"
    ),
    (
        "CREATE TABLE IF NOT EXISTS edge("
        "id INTEGER NOT NULL, type INTEGER NOT NULL, source_node_id INTEGER NOT NULL, "
        "target_node_id INTEGER NOT NULL, PRIMARY KEY(id), "
        "FOREIGN KEY(id) REFERENCES element(id) ON DELETE CASCADE, "
        "FOREIGN KEY(source_node_id) REFERENCES node(id) ON DELETE CASCADE, "
        "FOREIGN KEY(target_node_id) REFERENCES node(id) ON DELETE CASCADE);"
    ),
    (
        "CREATE TABLE IF NOT EXISTS node("
        "id INTEGER NOT NULL, type INTEGER NOT NULL, serialized_name TEXT, PRIMARY KEY(id), "
        "FOREIGN KEY(id) REFERENCES element(id) ON DELETE CASCADE);"
    ),
    (
        "CREATE TABLE IF NOT EXISTS symbol("
        "id INTEGER NOT NULL, definition_kind INTEGER NOT NULL, PRIMARY KEY(id), "
        "FOREIGN KEY(id) REFERENCES node(id) ON DELETE CASCADE);"
    ),
    (
        "CREATE TABLE IF NOT EXISTS file("
        "id INTEGER NOT NULL, path TEXT, language TEXT, modification_time TEXT, indexed INTEGER, "
        "complete INTEGER, line_count INTEGER, PRIMARY KEY(id), "
        "FOREIGN KEY(id) REFERENCES node(id) ON DELETE CASCADE);"
    ),
    (
        "CREATE TABLE IF NOT EXISTS filecontent("
        "id INTEGER, content TEXT, PRIMARY KEY(id), "
        "FOREIGN KEY(id) REFERENCES file(id) ON DELETE CASCADE ON UPDATE CASCADE);"
    ),
    (
        "CREATE TABLE IF NOT EXISTS node_file("
        "node_id INTEGER NOT NULL, file_node_id INTEGER NOT NULL, "
        "PRIMARY KEY(node_id, file_node_id), "
        "FOREIGN KEY(node_id) REFERENCES node(id) ON DELETE CASCADE, "
        "FOREIGN KEY(file_node_id) REFERENCES file(id) ON DELETE CASCADE);"
    ),
    (
        "CREATE TABLE IF NOT EXISTS local_symbol("
        "id INTEGER NOT NULL, name TEXT, PRIMARY KEY(id), "
        "FOREIGN KEY(id) REFERENCES element(id) ON DELETE CASCADE);"
    ),
    (
        "CREATE TABLE IF NOT EXISTS source_location("
        "id INTEGER NOT NULL, file_node_id INTEGER, start_line INTEGER, start_column INTEGER, "
        "end_line INTEGER, end_column INTEGER, type INTEGER, PRIMARY KEY(id), "
        "FOREIGN KEY(file_node_id) REFERENCES node(id) ON DELETE CASCADE);"
    ),
    (
        "CREATE TABLE IF NOT EXISTS occurrence("
        "element_id INTEGER NOT NULL, source_location_id INTEGER NOT NULL, "
        "PRIMARY KEY(element_id, source_location_id), "
        "FOREIGN KEY(element_id) REFERENCES element(id) ON DELETE CASCADE, "
        "FOREIGN KEY(source_location_id) REFERENCES source_location(id) ON DELETE CASCADE);"
    ),
    (
        "CREATE TABLE IF NOT EXISTS component_access("
        "node_id INTEGER NOT NULL, type INTEGER NOT NULL, PRIMARY KEY(node_id), "
        "FOREIGN KEY(node_id) REFERENCES node(id) ON DELETE CASCADE);"
    ),
    (
        "CREATE TABLE IF NOT EXISTS error("
        "id INTEGER NOT NULL, message TEXT, fatal INTEGER NOT NULL, indexed INTEGER NOT NULL, "
        "translation_unit TEXT, PRIMARY KEY(id), "
        "FOREIGN KEY(id) REFERENCES element(id) ON DELETE CASCADE);"
    ),
)

INDEX_SQL = (
    "CREATE INDEX IF NOT EXISTS edge_source_node_id_index ON edge(source_node_id);",
    "CREATE INDEX IF NOT EXISTS edge_target_node_id_index ON edge(target_node_id);",
    "CREATE INDEX IF NOT EXISTS node_serialized_name_index ON node(serialized_name);",
    (
        "CREATE INDEX IF NOT EXISTS source_location_file_node_id_index "
        "ON source_location(file_node_id);"
    ),
    "CREATE INDEX IF NOT EXISTS file_path_index ON file(path);",
    "CREATE INDEX IF NOT EXISTS node_file_file_node_id_index ON node_file(file_node_id);",
    "CREATE INDEX IF NOT EXISTS occurrence_element_id_index ON occurrence(element_id);",
    (
        "CREATE INDEX IF NOT EXISTS occurrence_source_location_id_index "
        "ON occurrence(source_location_id);"
    ),
)

EXTENSION_SQL = (
    (
        "CREATE TABLE IF NOT EXISTS edge_extension("
        "edge_id INTEGER NOT NULL, kind TEXT NOT NULL, metadata TEXT, "
        "FOREIGN KEY(edge_id) REFERENCES edge(id) ON DELETE CASCADE);"
    ),
    "CREATE INDEX IF NOT EXISTS idx_edge_extension_edge_id ON edge_extension(edge_id);",
    (
        "CREATE TABLE IF NOT EXISTS node_extension("
        "node_id INTEGER NOT NULL, kind TEXT NOT NULL, confidence REAL, metadata TEXT, "
        "FOREIGN KEY(node_id) REFERENCES node(id) ON DELETE CASCADE);"
    ),
    "CREATE INDEX IF NOT EXISTS idx_node_extension_node_id ON node_extension(node_id);",
)

NODE_KIND_VALUES = {node_type.name: int(node_type) for node_type in NodeType}
EDGE_TYPE_VALUES = {edge_type.name: int(edge_type) for edge_type in EdgeType}
DEFINITION_KIND_VALUES = {
    definition_kind.name: int(definition_kind) for definition_kind in DefinitionKind
}
SOURCE_LOCATION_VALUES = {
    location_type.name: int(location_type) for location_type in SourceLocationType
}
ACCESS_KIND_VALUES = {access_kind.name: int(access_kind) for access_kind in AccessKind}


def create_schema(connection: sqlite3.Connection, include_extensions: bool = True) -> None:
    """Create the core SourcetrailDB schema in the provided database."""
    for statement in SCHEMA_SQL:
        connection.execute(statement)
    for statement in INDEX_SQL:
        connection.execute(statement)
    if include_extensions:
        for statement in EXTENSION_SQL:
            connection.execute(statement)
    connection.commit()


def ensure_tables(
    connection: sqlite3.Connection,
    expected: Iterable[str] = REQUIRED_TABLES,
) -> list[str]:
    """Return missing table names from the current database."""
    existing = {
        row[0]
        for row in connection.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table' AND name NOT LIKE 'sqlite_%';"
        )
    }
    return [table for table in expected if table not in existing]
