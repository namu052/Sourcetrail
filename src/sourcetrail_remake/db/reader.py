"""Read helpers for Sourcetrail-compatible index files."""

from __future__ import annotations

import sqlite3
from pathlib import Path

from sourcetrail_remake.core.types import DatabaseSummary, NodeId, SourceLocation, SourceLocationType


class DatabaseReader:
    """Read project summaries, symbols, and occurrences from a generated DB."""

    def __init__(self, db_path: Path):
        self.db_path = Path(db_path).resolve()

    def summary(self) -> DatabaseSummary:
        with sqlite3.connect(self.db_path) as connection:
            return DatabaseSummary(
                files=self._count(connection, "file"),
                symbols=self._count(connection, "symbol"),
                edges=self._count(connection, "edge"),
                locations=self._count(connection, "source_location"),
                occurrences=self._count(connection, "occurrence"),
                unsolved=int(
                    connection.execute(
                        "SELECT COUNT(*) FROM node_extension WHERE kind = 'unsolved';"
                    ).fetchone()[0]
                ),
            )

    def read_meta(self) -> dict[str, str]:
        with sqlite3.connect(self.db_path) as connection:
            rows = connection.execute("SELECT key, value FROM meta;").fetchall()
        return {key: value for key, value in rows}

    def find_symbol_id(self, serialized_name: str) -> NodeId | None:
        with sqlite3.connect(self.db_path) as connection:
            row = connection.execute(
                "SELECT id FROM node WHERE serialized_name = ? ORDER BY id LIMIT 1;",
                (serialized_name,),
            ).fetchone()
        return None if row is None else NodeId(int(row[0]))

    def list_unsolved(self) -> list[tuple[NodeId, str]]:
        with sqlite3.connect(self.db_path) as connection:
            rows = connection.execute(
                (
                    "SELECT node.id, node.serialized_name "
                    "FROM node "
                    "INNER JOIN node_extension ON node_extension.node_id = node.id "
                    "WHERE node_extension.kind = 'unsolved' "
                    "ORDER BY node.id;"
                )
            ).fetchall()
        return [(NodeId(int(row[0])), str(row[1])) for row in rows]

    def get_occurrences(self, element_id: NodeId) -> list[SourceLocation]:
        with sqlite3.connect(self.db_path) as connection:
            rows = connection.execute(
                (
                    "SELECT source_location.start_line, source_location.start_column, "
                    "source_location.end_line, source_location.end_column, source_location.type "
                    "FROM occurrence "
                    "INNER JOIN source_location ON source_location.id = occurrence.source_location_id "
                    "WHERE occurrence.element_id = ? "
                    "ORDER BY source_location.id;"
                ),
                (int(element_id),),
            ).fetchall()
        return [
            SourceLocation(
                start_line=int(row[0]),
                start_column=int(row[1]),
                end_line=int(row[2]),
                end_column=int(row[3]),
                type=SourceLocationType(int(row[4])),
            )
            for row in rows
        ]

    def _count(self, connection: sqlite3.Connection, table: str) -> int:
        row = connection.execute(f"SELECT COUNT(*) FROM {table};").fetchone()
        assert row is not None
        return int(row[0])


def read_meta(db_path: Path) -> dict[str, str]:
    """Return the current meta key/value mapping."""
    return DatabaseReader(db_path).read_meta()
