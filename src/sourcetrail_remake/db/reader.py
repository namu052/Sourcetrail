"""Read helpers for Sourcetrail-compatible index files."""

from __future__ import annotations

import sqlite3
from pathlib import Path

from sourcetrail_remake.core.types import (
    DatabaseSummary,
    EdgeId,
    EdgeType,
    GraphEdgeRecord,
    GraphNeighborhood,
    GraphNodeRecord,
    NodeId,
    NodeType,
    SourceLocation,
    SourceLocationType,
    SymbolContext,
)


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

    def get_symbol(self, symbol_id: NodeId) -> GraphNodeRecord | None:
        with sqlite3.connect(self.db_path) as connection:
            nodes = self._load_nodes(connection, {int(symbol_id)})
        return nodes[0] if nodes else None

    def list_symbols(
        self,
        *,
        limit: int | None = None,
        include_files: bool = False,
    ) -> tuple[GraphNodeRecord, ...]:
        query = "SELECT id FROM node "
        parameters: list[int] = []
        if not include_files:
            query += "WHERE type != ? "
            parameters.append(int(NodeType.NODE_FILE))
        query += "ORDER BY serialized_name"
        if limit is not None:
            query += " LIMIT ?"
            parameters.append(limit)

        with sqlite3.connect(self.db_path) as connection:
            node_ids = {int(row[0]) for row in connection.execute(query, parameters).fetchall()}
            return self._load_nodes(connection, node_ids)

    def list_unsolved(self) -> list[tuple[NodeId, str]]:
        with sqlite3.connect(self.db_path) as connection:
            rows = connection.execute(
                "SELECT node.id, node.serialized_name "
                "FROM node "
                "INNER JOIN node_extension ON node_extension.node_id = node.id "
                "WHERE node_extension.kind = 'unsolved' "
                "ORDER BY node.id;"
            ).fetchall()
        return [(NodeId(int(row[0])), str(row[1])) for row in rows]

    def get_occurrences(self, element_id: NodeId) -> list[SourceLocation]:
        with sqlite3.connect(self.db_path) as connection:
            rows = connection.execute(
                (
                    "SELECT source_location.start_line, source_location.start_column, "
                    "source_location.end_line, source_location.end_column, source_location.type "
                    "FROM occurrence "
                    "INNER JOIN source_location "
                    "ON source_location.id = occurrence.source_location_id "
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

    def find_context_at(self, file: str | Path, line: int, column: int) -> SymbolContext | None:
        """Return the best symbol declaration context for a cursor position."""
        file_path = Path(file).resolve()
        with sqlite3.connect(self.db_path) as connection:
            file_row = connection.execute(
                (
                    "SELECT file.id, file.path, filecontent.content "
                    "FROM file "
                    "LEFT JOIN filecontent ON filecontent.id = file.id "
                    "WHERE file.path = ? "
                    "LIMIT 1;"
                ),
                (str(file_path),),
            ).fetchone()
            if file_row is None:
                return None

            file_id = int(file_row[0])
            source = "" if file_row[2] is None else str(file_row[2])
            symbol_id, location = self._find_context_symbol(connection, file_id, line, column)
            if symbol_id is None or location is None:
                return None

            breadcrumb_ids = self._collect_breadcrumb_ids(connection, symbol_id)
            nodes = {
                int(node.id): node
                for node in self._load_nodes(connection, {int(symbol_id), *breadcrumb_ids})
            }
            node = nodes.get(int(symbol_id))
            if node is None:
                return None
            breadcrumbs = tuple(nodes[node_id] for node_id in breadcrumb_ids if node_id in nodes)
            return SymbolContext(
                node=node,
                file_path=Path(str(file_row[1])),
                location=location,
                source=source,
                breadcrumbs=breadcrumbs,
            )

    def load_graph(self, symbol_id: NodeId, depth: int) -> GraphNeighborhood:
        with sqlite3.connect(self.db_path) as connection:
            node_ids, edges = self._collect_neighborhood(connection, symbol_id, depth)
            nodes = self._load_nodes(connection, node_ids)
        return GraphNeighborhood(
            root_id=symbol_id,
            depth=max(depth, 0),
            nodes=nodes,
            edges=edges,
        )

    def _count(self, connection: sqlite3.Connection, table: str) -> int:
        row = connection.execute(f"SELECT COUNT(*) FROM {table};").fetchone()
        assert row is not None
        return int(row[0])

    def _collect_neighborhood(
        self,
        connection: sqlite3.Connection,
        symbol_id: NodeId,
        depth: int,
    ) -> tuple[set[int], tuple[GraphEdgeRecord, ...]]:
        node_ids = {int(symbol_id)}
        visited_edges: dict[int, GraphEdgeRecord] = {}
        frontier = {int(symbol_id)}

        for _ in range(max(depth, 0)):
            if not frontier:
                break
            rows = self._fetch_connected_edges(connection, frontier)
            next_frontier: set[int] = set()
            for row in rows:
                edge_id = int(row[0])
                if edge_id in visited_edges:
                    continue
                source = int(row[2])
                target = int(row[3])
                visited_edges[edge_id] = GraphEdgeRecord(
                    id=EdgeId(edge_id),
                    source=NodeId(source),
                    target=NodeId(target),
                    edge_type=EdgeType(int(row[1])),
                )
                if source not in node_ids:
                    next_frontier.add(source)
                    node_ids.add(source)
                if target not in node_ids:
                    next_frontier.add(target)
                    node_ids.add(target)
            frontier = next_frontier

        return node_ids, tuple(visited_edges[edge_id] for edge_id in sorted(visited_edges))

    def _find_context_symbol(
        self,
        connection: sqlite3.Connection,
        file_id: int,
        line: int,
        column: int,
    ) -> tuple[NodeId | None, SourceLocation | None]:
        exact_row = connection.execute(
            (
                "SELECT node.id, source_location.start_line, source_location.start_column, "
                "source_location.end_line, source_location.end_column, source_location.type "
                "FROM occurrence "
                "INNER JOIN source_location "
                "ON source_location.id = occurrence.source_location_id "
                "INNER JOIN node ON node.id = occurrence.element_id "
                "INNER JOIN symbol ON symbol.id = node.id "
                "WHERE source_location.file_node_id = ? "
                "AND (source_location.start_line < ? "
                "OR (source_location.start_line = ? AND source_location.start_column <= ?)) "
                "AND (source_location.end_line > ? "
                "OR (source_location.end_line = ? AND source_location.end_column >= ?)) "
                "ORDER BY (source_location.end_line - source_location.start_line) ASC, "
                "(source_location.end_column - source_location.start_column) ASC, node.id ASC "
                "LIMIT 1;"
            ),
            (file_id, line, line, column, line, line, column),
        ).fetchone()
        if exact_row is not None:
            return self._row_to_context_location(exact_row)

        preceding_row = connection.execute(
            (
                "SELECT node.id, source_location.start_line, source_location.start_column, "
                "source_location.end_line, source_location.end_column, source_location.type "
                "FROM occurrence "
                "INNER JOIN source_location "
                "ON source_location.id = occurrence.source_location_id "
                "INNER JOIN node ON node.id = occurrence.element_id "
                "INNER JOIN symbol ON symbol.id = node.id "
                "WHERE source_location.file_node_id = ? "
                "AND source_location.start_line <= ? "
                "ORDER BY source_location.start_line DESC, source_location.start_column DESC "
                "LIMIT 1;"
            ),
            (file_id, line),
        ).fetchone()
        if preceding_row is None:
            return None, None
        return self._row_to_context_location(preceding_row)

    def _row_to_context_location(
        self, row: sqlite3.Row | tuple[int, int, int, int, int, int]
    ) -> tuple[NodeId, SourceLocation]:
        return (
            NodeId(int(row[0])),
            SourceLocation(
                start_line=int(row[1]),
                start_column=int(row[2]),
                end_line=int(row[3]),
                end_column=int(row[4]),
                type=SourceLocationType(int(row[5])),
            ),
        )

    def _collect_breadcrumb_ids(
        self, connection: sqlite3.Connection, symbol_id: NodeId
    ) -> tuple[int, ...]:
        breadcrumbs: list[int] = []
        current_id = int(symbol_id)
        while True:
            row = connection.execute(
                "SELECT source_node_id FROM edge WHERE type = ? AND target_node_id = ? LIMIT 1;",
                (int(EdgeType.EDGE_MEMBER), current_id),
            ).fetchone()
            if row is None:
                break
            current_id = int(row[0])
            breadcrumbs.append(current_id)
        breadcrumbs.reverse()
        return tuple(breadcrumbs)

    def _fetch_connected_edges(
        self,
        connection: sqlite3.Connection,
        frontier: set[int],
    ) -> list[tuple[int, int, int, int]]:
        placeholders = ", ".join("?" for _ in frontier)
        rows = connection.execute(
            (
                "SELECT id, type, source_node_id, target_node_id "
                f"FROM edge WHERE source_node_id IN ({placeholders}) "
                f"OR target_node_id IN ({placeholders}) "
                "ORDER BY id;"
            ),
            [*frontier, *frontier],
        ).fetchall()
        return [(int(row[0]), int(row[1]), int(row[2]), int(row[3])) for row in rows]

    def _load_nodes(
        self,
        connection: sqlite3.Connection,
        node_ids: set[int],
    ) -> tuple[GraphNodeRecord, ...]:
        if not node_ids:
            return ()

        member_counts = {
            int(row[0]): int(row[1])
            for row in connection.execute(
                (
                    "SELECT source_node_id, COUNT(*) "
                    "FROM edge "
                    "WHERE type = ? "
                    "GROUP BY source_node_id;"
                ),
                (int(EdgeType.EDGE_MEMBER),),
            ).fetchall()
        }
        parent_ids = {
            int(row[0]): NodeId(int(row[1]))
            for row in connection.execute(
                ("SELECT target_node_id, source_node_id FROM edge WHERE type = ?;"),
                (int(EdgeType.EDGE_MEMBER),),
            ).fetchall()
        }
        placeholders = ", ".join("?" for _ in node_ids)
        rows = connection.execute(
            (
                "SELECT node.id, node.type, node.serialized_name, "
                "CASE WHEN node_extension.node_id IS NULL THEN 0 ELSE 1 END "
                f"FROM node "
                "LEFT JOIN node_extension "
                "ON node_extension.node_id = node.id AND node_extension.kind = 'unsolved' "
                f"WHERE node.id IN ({placeholders}) "
                "ORDER BY node.id;"
            ),
            list(node_ids),
        ).fetchall()
        return tuple(
            GraphNodeRecord(
                id=NodeId(int(row[0])),
                serialized_name=str(row[2]),
                display_name=self._display_name(str(row[2]), NodeType(int(row[1]))),
                node_type=NodeType(int(row[1])),
                member_count=member_counts.get(int(row[0]), 0),
                is_unsolved=bool(int(row[3])),
                parent_id=parent_ids.get(int(row[0])),
            )
            for row in rows
        )

    def _display_name(self, serialized_name: str, node_type: NodeType) -> str:
        if node_type == NodeType.NODE_FILE:
            return Path(serialized_name).name
        return serialized_name.rsplit(".", maxsplit=1)[-1]


def read_meta(db_path: Path) -> dict[str, str]:
    """Return the current meta key/value mapping."""
    return DatabaseReader(db_path).read_meta()
