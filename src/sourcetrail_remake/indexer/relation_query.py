"""Directional relation queries over the Sourcetrail-compatible edge tables."""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from sourcetrail_remake.core.types import EdgeType, NodeId, NodeType


@dataclass(frozen=True, slots=True)
class Relation:
    """A related symbol returned for a relation axis."""

    node_id: NodeId
    serialized_name: str
    display_name: str
    node_type: NodeType
    edge_type: EdgeType
    depth: int
    is_recursive: bool = False


@dataclass(frozen=True, slots=True)
class Occurrence:
    """A source occurrence used by the References axis."""

    element_id: int
    file_path: Path | None
    start_line: int
    start_column: int
    end_line: int
    end_column: int
    label: str


class RelationQuery:
    """Read call, reference, and override relations from a generated database."""

    def __init__(self, db_path: Path):
        self.db_path = Path(db_path).resolve()

    def get_callers(self, node_id: NodeId, depth: int = 3) -> list[Relation]:
        """Return incoming call edges up to the requested depth."""
        return self._walk_edges(
            node_id,
            edge_type=EdgeType.EDGE_CALL,
            direction="incoming",
            depth=depth,
        )

    def get_callees(self, node_id: NodeId, depth: int = 3) -> list[Relation]:
        """Return outgoing call edges up to the requested depth."""
        return self._walk_edges(
            node_id,
            edge_type=EdgeType.EDGE_CALL,
            direction="outgoing",
            depth=depth,
        )

    def get_references(self, node_id: NodeId) -> list[Occurrence]:
        """Return direct occurrences for a symbol plus incoming usage edges."""
        with sqlite3.connect(self.db_path) as connection:
            occurrence_rows = connection.execute(
                (
                    "SELECT occurrence.element_id, file.path, source_location.start_line, "
                    "source_location.start_column, source_location.end_line, "
                    "source_location.end_column, node.serialized_name "
                    "FROM occurrence "
                    "INNER JOIN source_location "
                    "ON source_location.id = occurrence.source_location_id "
                    "LEFT JOIN file ON file.id = source_location.file_node_id "
                    "LEFT JOIN node ON node.id = occurrence.element_id "
                    "WHERE occurrence.element_id = ? "
                    "ORDER BY source_location.start_line, source_location.start_column;"
                ),
                (int(node_id),),
            ).fetchall()
            usage_rows = connection.execute(
                (
                    "SELECT edge.id, file.path, source_location.start_line, "
                    "source_location.start_column, source_location.end_line, "
                    "source_location.end_column, node.serialized_name "
                    "FROM edge "
                    "LEFT JOIN occurrence ON occurrence.element_id = edge.id "
                    "LEFT JOIN source_location "
                    "ON source_location.id = occurrence.source_location_id "
                    "LEFT JOIN file ON file.id = source_location.file_node_id "
                    "INNER JOIN node ON node.id = edge.source_node_id "
                    "WHERE edge.target_node_id = ? AND edge.type IN (?, ?) "
                    "ORDER BY source_location.start_line, source_location.start_column;"
                ),
                (int(node_id), int(EdgeType.EDGE_USAGE), int(EdgeType.EDGE_TYPE_USAGE)),
            ).fetchall()
        return [self._row_to_occurrence(row) for row in [*occurrence_rows, *usage_rows]]

    def get_overrides(self, node_id: NodeId) -> list[NodeId]:
        """Return directly connected override nodes in both directions."""
        with sqlite3.connect(self.db_path) as connection:
            rows = connection.execute(
                (
                    "SELECT CASE WHEN source_node_id = ? "
                    "THEN target_node_id ELSE source_node_id END "
                    "FROM edge "
                    "WHERE type = ? AND (source_node_id = ? OR target_node_id = ?) "
                    "ORDER BY id;"
                ),
                (int(node_id), int(EdgeType.EDGE_OVERRIDE), int(node_id), int(node_id)),
            ).fetchall()
        return [NodeId(int(row[0])) for row in rows]

    def get_override_relations(self, node_id: NodeId, depth: int = 3) -> list[Relation]:
        """Return override and inheritance relations as UI-ready records."""
        override_relations = self._walk_edges(
            node_id,
            edge_type=EdgeType.EDGE_OVERRIDE,
            direction="both",
            depth=depth,
        )
        inheritance_relations = self._walk_edges(
            node_id,
            edge_type=EdgeType.EDGE_INHERITANCE,
            direction="both",
            depth=depth,
        )
        return [*override_relations, *inheritance_relations]

    def _walk_edges(
        self,
        node_id: NodeId,
        *,
        edge_type: EdgeType,
        direction: str,
        depth: int,
    ) -> list[Relation]:
        max_depth = max(depth, 0)
        results: list[Relation] = []
        frontier: list[tuple[int, int, tuple[int, ...]]] = [(int(node_id), 0, (int(node_id),))]
        with sqlite3.connect(self.db_path) as connection:
            while frontier:
                current_id, current_depth, path = frontier.pop(0)
                if current_depth >= max_depth:
                    continue
                rows = self._fetch_edge_rows(connection, current_id, edge_type, direction)
                for row in rows:
                    related_id = int(row[0])
                    is_recursive = related_id in path
                    relation = self._load_relation(
                        connection,
                        related_id,
                        edge_type,
                        current_depth + 1,
                        is_recursive=is_recursive,
                    )
                    if relation is None:
                        continue
                    results.append(relation)
                    if not is_recursive:
                        frontier.append((related_id, current_depth + 1, (*path, related_id)))
        return results

    def _fetch_edge_rows(
        self,
        connection: sqlite3.Connection,
        node_id: int,
        edge_type: EdgeType,
        direction: str,
    ) -> list[tuple[int]]:
        if direction == "incoming":
            query = (
                "SELECT source_node_id FROM edge WHERE target_node_id = ? AND type = ? ORDER BY id;"
            )
            parameters: tuple[int, ...] = (node_id, int(edge_type))
        elif direction == "outgoing":
            query = (
                "SELECT target_node_id FROM edge WHERE source_node_id = ? AND type = ? ORDER BY id;"
            )
            parameters = (node_id, int(edge_type))
        else:
            query = (
                "SELECT CASE WHEN source_node_id = ? THEN target_node_id ELSE source_node_id END "
                "FROM edge WHERE type = ? AND (source_node_id = ? OR target_node_id = ?) "
                "ORDER BY id;"
            )
            parameters = (node_id, int(edge_type), node_id, node_id)
        return [(int(row[0]),) for row in connection.execute(query, parameters).fetchall()]

    def _load_relation(
        self,
        connection: sqlite3.Connection,
        node_id: int,
        edge_type: EdgeType,
        depth: int,
        *,
        is_recursive: bool,
    ) -> Relation | None:
        row = connection.execute(
            "SELECT id, type, serialized_name FROM node WHERE id = ? LIMIT 1;",
            (node_id,),
        ).fetchone()
        if row is None:
            return None
        serialized_name = str(row[2])
        return Relation(
            node_id=NodeId(int(row[0])),
            serialized_name=serialized_name,
            display_name=serialized_name.rsplit(".", maxsplit=1)[-1],
            node_type=NodeType(int(row[1])),
            edge_type=edge_type,
            depth=depth,
            is_recursive=is_recursive,
        )

    def _row_to_occurrence(self, row: sqlite3.Row | tuple[Any, ...]) -> Occurrence:
        file_path = None if row[1] is None else Path(str(row[1]))
        label = "<unknown>" if row[6] is None else str(row[6]).rsplit(".", maxsplit=1)[-1]
        return Occurrence(
            element_id=_to_int(row[0]),
            file_path=file_path,
            start_line=0 if row[2] is None else _to_int(row[2]),
            start_column=0 if row[3] is None else _to_int(row[3]),
            end_line=0 if row[4] is None else _to_int(row[4]),
            end_column=0 if row[5] is None else _to_int(row[5]),
            label=label,
        )


def _to_int(value: object) -> int:
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        return int(value)
    raise TypeError(f"Expected int-compatible DB value, got {type(value)!r}")
