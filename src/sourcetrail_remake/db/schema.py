"""SourcetrailDB v25 schema constants for Phase 0."""

from __future__ import annotations

import sqlite3
from collections.abc import Iterable

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
    "local_symbol",
    "source_location",
    "occurrence",
    "component_access",
    "error",
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
)

NODE_KIND_VALUES = {
    "NODE_SYMBOL": 1 << 0,
    "NODE_TYPE": 1 << 1,
    "NODE_BUILTIN_TYPE": 1 << 2,
    "NODE_MODULE": 1 << 3,
    "NODE_NAMESPACE": 1 << 4,
    "NODE_PACKAGE": 1 << 5,
    "NODE_STRUCT": 1 << 6,
    "NODE_CLASS": 1 << 7,
    "NODE_INTERFACE": 1 << 8,
    "NODE_ANNOTATION": 1 << 9,
    "NODE_GLOBAL_VARIABLE": 1 << 10,
    "NODE_FIELD": 1 << 11,
    "NODE_FUNCTION": 1 << 12,
    "NODE_METHOD": 1 << 13,
    "NODE_ENUM": 1 << 14,
    "NODE_ENUM_CONSTANT": 1 << 15,
    "NODE_TYPEDEF": 1 << 16,
    "NODE_TYPE_PARAMETER": 1 << 17,
    "NODE_FILE": 1 << 18,
    "NODE_MACRO": 1 << 19,
    "NODE_UNION": 1 << 20,
}

EDGE_TYPE_VALUES = {
    "EDGE_UNDEFINED": 0,
    "EDGE_MEMBER": 1 << 0,
    "EDGE_TYPE_USAGE": 1 << 1,
    "EDGE_USAGE": 1 << 2,
    "EDGE_CALL": 1 << 3,
    "EDGE_INHERITANCE": 1 << 4,
    "EDGE_OVERRIDE": 1 << 5,
    "EDGE_TYPE_ARGUMENT": 1 << 6,
    "EDGE_TEMPLATE_SPECIALIZATION": 1 << 7,
    "EDGE_INCLUDE": 1 << 8,
    "EDGE_IMPORT": 1 << 9,
    "EDGE_BUNDLED_EDGES": 1 << 10,
    "EDGE_MACRO_USAGE": 1 << 11,
    "EDGE_ANNOTATION_USAGE": 1 << 12,
}

DEFINITION_KIND_VALUES = {
    "DEFINITION_NONE": 0,
    "DEFINITION_IMPLICIT": 1,
    "DEFINITION_EXPLICIT": 2,
}

SOURCE_LOCATION_VALUES = {
    "LOCATION_TOKEN": 0,
    "LOCATION_SCOPE": 1,
    "LOCATION_QUALIFIER": 2,
    "LOCATION_LOCAL_SYMBOL": 3,
    "LOCATION_SIGNATURE": 4,
    "LOCATION_COMMENT": 5,
    "LOCATION_ERROR": 6,
    "LOCATION_FULLTEXT_SEARCH": 7,
    "LOCATION_SCREEN_SEARCH": 8,
    "LOCATION_UNSOLVED": 9,
}

ACCESS_KIND_VALUES = {
    "ACCESS_NONE": 0,
    "ACCESS_PUBLIC": 1,
    "ACCESS_PROTECTED": 2,
    "ACCESS_PRIVATE": 3,
    "ACCESS_DEFAULT": 4,
    "ACCESS_TEMPLATE_PARAMETER": 5,
    "ACCESS_TYPE_PARAMETER": 6,
}


def create_schema(connection: sqlite3.Connection, include_extensions: bool = True) -> None:
    """Create the core SourcetrailDB schema in the provided database."""
    for statement in SCHEMA_SQL:
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
